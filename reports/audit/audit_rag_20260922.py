"""Auditoría local sin red ni escrituras sobre Chroma; solo biblioteca estándar.

Los probes reproducen comportamientos, no sustituyen pytest ni un ensayo RAG real.
Para dos clases con dependencias ausentes se carga su AST sin imports y se inyectan
dobles explícitos. Sus métodos conservan el código original del repositorio.
"""
from __future__ import annotations

import ast
import json
import re
import runpy
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src.core.interfaces import BaseRetriever
from src.validation.citation_validator import CitationSourceValidator

PromptBuilder = runpy.run_path(str(ROOT / "src/generation/prompt_builder.py"))["PromptBuilder"]
SemanticHardwareChunker = runpy.run_path(str(ROOT / "src/indexing/chunker.py"))["SemanticHardwareChunker"]
DocumentCleaner = runpy.run_path(str(ROOT / "src/ingestion/document_cleaner.py"))["DocumentCleaner"]
MetadataExtractor = runpy.run_path(str(ROOT / "src/ingestion/metadata_extractor.py"))["MetadataExtractor"]


def isolated_class(relative_path, name, dependencies):
    tree = ast.parse((ROOT / relative_path).read_text(encoding="utf-8-sig"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), cls], type_ignores=[])
    scope = dict(dependencies)
    exec(compile(ast.fix_missing_locations(module), str(ROOT / relative_path), "exec"), scope)
    return scope[name]


def audit():
    result = {"scope": "Offline; SQLite read-only; isolated probes; no API calls"}
    result["inventory"] = {
        "raw_pdfs": len(list((ROOT / "data/raw").rglob("*.pdf"))),
        "processed_documents": len(list((ROOT / "data/processed").rglob("*.md"))),
    }
    db = ROOT / "storage/vector_store/chroma.sqlite3"
    with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as conn:
        result["collections"] = conn.execute("select name, dimension from collections").fetchall()
        result["indexed_chunks"] = conn.execute("select count(*) from embeddings").fetchone()[0]
        result["indexed_documents"] = conn.execute("select string_value,count(*) from embedding_metadata where key='file_name' group by string_value").fetchall()
        result["metadata_keys"] = [r[0] for r in conn.execute("select distinct key from embedding_metadata")]
        stored_text = dict(conn.execute("select e.embedding_id,m.string_value from embeddings e join embedding_metadata m on e.id=m.id where m.key='chroma:document'"))

    # Only non-secret configuration keys are exposed. No dotenv interpolation.
    allowed = {"EMBEDDING_PROVIDER", "DEFAULT_EMBEDDING_MODEL", "EMBEDDING_DIMENSION", "ALLOW_TEST_EMBEDDINGS", "DEFAULT_LLM_MODEL", "GEMINI_MODEL", "DEFAULT_TEMPERATURE", "TEMPERATURE", "TOP_K_RETRIEVAL", "CHUNK_SIZE", "CHUNK_OVERLAP"}
    config = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() in allowed:
            config[key.strip()] = value.strip()
    result["env_file_non_secret_values"] = config
    current_chunker = SemanticHardwareChunker(chunk_size=int(config.get("CHUNK_SIZE", 800)), chunk_overlap=int(config.get("CHUNK_OVERLAP", 150)))
    comparison = []
    for path in sorted((ROOT / "data/processed").rglob("*.md")):
        clean = DocumentCleaner().clean(path.read_text(encoding="utf-8"))
        meta = MetadataExtractor().extract_metadata(clean, path.name, ROOT / "data/metadata" / path.parent.name / (path.stem + ".json"))
        fresh = current_chunker.chunk(clean, metadata=meta)
        comparison.append({"file": path.name, "fresh_chunks": len(fresh), "matching_id_and_text": sum(stored_text.get(c["chunk_id"]) == c["text"] for c in fresh)})
    result["current_pipeline_vs_stored_text"] = comparison

    probes = {}
    raw = "Parámetro\nValor\n16\nUnidad\nMHz"
    cleaned = DocumentCleaner().clean(raw)
    probes["numeric_line_removed"] = {"input": raw, "output": cleaned, "observed": "16" not in cleaned}

    validation = CitationSourceValidator().validate_citations(
        "La memoria es 999 TB.",
        [{"text": "La memoria es 2 KB.", "metadata": {"file_name": "fixture.md"}}],
    )
    probes["contradictory_claim_accepted"] = {"valid": validation["valid"], "confidence": validation["confidence_score"]}

    hybrid = isolated_class("src/retrieval/hybrid_search.py", "HybridSearchEngine", {
        "BaseRetriever": BaseRetriever, "re": re,
        "get_settings": lambda: SimpleNamespace(HYBRID_ALPHA=0.5),
    })
    indexer = Mock()
    indexer.search.return_value = []
    embedder = Mock()
    embedder.get_query_embedding.return_value = [1.0]
    engine = hybrid(vector_indexer=indexer, embedder=embedder)
    engine.corpus_chunks = [{"chunk_id": "arduino_fixture", "text": "Arduino PWM", "metadata": {"category": "Arduino"}}]
    engine.bm25 = Mock()
    engine.bm25.get_scores.return_value = [1.0]
    hits = engine.search("PWM", filters={"category": "ESP32"}, top_k=1)
    probes["lexical_filter_leak"] = {"requested_category": "ESP32", "returned": hits, "scoring": "mock BM25 score=1; dense results empty"}

    generator_cls = isolated_class("src/generation/response_generator.py", "ResponseGenerator", {
        "get_settings": lambda: SimpleNamespace(), "PromptBuilder": PromptBuilder,
    })
    client = Mock(model_name="offline-test", temperature=0)
    client.generate.return_value = "Respuesta simulada"
    generator = generator_cls(gemini_client=client)
    empty = generator.generate_response("Pregunta", chunks=[{"text": "", "metadata": {"file_name": "empty.md"}}])
    probes["empty_chunk_calls_generator"] = {"calls": client.generate.call_count, "context": empty.get("context")}

    chunker = SemanticHardwareChunker(chunk_size=80, chunk_overlap=10)
    table = "| Registro | Valor |\n|---|---|\n" + "| REGISTRO | 12345 |\n" * 12
    chunks = chunker.chunk(table, {"file_name": "table.md"})
    probes["long_table_loses_column_context"] = {"chunks": len(chunks), "without_column_header": sum("| Registro | Valor |" not in c["raw_text"] for c in chunks)}
    result["probes"] = probes

    files = [p for base in ("src", "configs", "tests") for p in (ROOT / base).rglob("*.py")]
    for path in files:
        compile(path.read_text(encoding="utf-8-sig"), str(path), "exec")
    result["syntax_files_checked"] = len(files)
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
