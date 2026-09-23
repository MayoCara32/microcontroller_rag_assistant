"""Script robusto para segmentar, vectorizar e indexar documentos restantes con manejo de rate limit (429)."""
import sys
import json
import time
from pathlib import Path

# Ajustar PYTHONPATH
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from src.indexing.chunker import SemanticHardwareChunker
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer

DOCUMENTS_TO_INDEX = [
    # Arduino
    {
        "pdf_name": "atmega328ds.pdf",
        "category": "Arduino",
        "md_path": "data/processed/arduino/atmega328ds.md",
        "json_path": "data/metadata/arduino/atmega328ds.json"
    },
    {
        "pdf_name": "atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.pdf",
        "category": "Arduino",
        "md_path": "data/processed/arduino/atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.md",
        "json_path": "data/metadata/arduino/atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.json"
    },
    # Electronica
    {
        "pdf_name": "L6-Timers-and-Interrupts.pdf",
        "category": "Electronica",
        "md_path": "data/processed/electronica/L6-Timers-and-Interrupts.md",
        "json_path": "data/metadata/electronica/L6-Timers-and-Interrupts.json"
    },
    {
        "pdf_name": "note_1474198148.pdf",
        "category": "Electronica",
        "md_path": "data/processed/electronica/note_1474198148.md",
        "json_path": "data/metadata/electronica/note_1474198148.json"
    },
    {
        "pdf_name": "tl5001a-q1.pdf",
        "category": "Electronica",
        "md_path": "data/processed/electronica/tl5001a-q1.md",
        "json_path": "data/metadata/electronica/tl5001a-q1.json"
    },
    # ESP32
    {
        "pdf_name": "esp-hardware-design-guidelines-en-master-esp32.pdf",
        "category": "ESP32",
        "md_path": "data/processed/esp32/esp-hardware-design-guidelines-en-master-esp32.md",
        "json_path": "data/metadata/esp32/esp-hardware-design-guidelines-en-master-esp32.json"
    },
    {
        "pdf_name": "esp32-pico_series_datasheet_en.pdf",
        "category": "ESP32",
        "md_path": "data/processed/esp32/esp32-pico_series_datasheet_en.md",
        "json_path": "data/metadata/esp32/esp32-pico_series_datasheet_en.json"
    },
    {
        "pdf_name": "esp32_technical_reference_manual_en.pdf",
        "category": "ESP32",
        "md_path": "data/processed/esp32/esp32_technical_reference_manual_en.md",
        "json_path": "data/metadata/esp32/esp32_technical_reference_manual_en.json"
    },
    # Protocolos
    {
        "pdf_name": "UM10204.pdf",
        "category": "Protocolos",
        "md_path": "data/processed/protocolos/UM10204.md",
        "json_path": "data/metadata/protocolos/UM10204.json"
    },
    {
        "pdf_name": "modbusprotocolspecification.pdf",
        "category": "Protocolos",
        "md_path": "data/processed/protocolos/modbusprotocolspecification.md",
        "json_path": "data/metadata/protocolos/modbusprotocolspecification.json"
    },
    {
        "pdf_name": "sboa621.pdf",
        "category": "Protocolos",
        "md_path": "data/processed/protocolos/sboa621.md",
        "json_path": "data/metadata/protocolos/sboa621.json"
    },
    {
        "pdf_name": "sprugp1.pdf",
        "category": "Protocolos",
        "md_path": "data/processed/protocolos/sprugp1.md",
        "json_path": "data/metadata/protocolos/sprugp1.json"
    },
    # Raspberry Pi
    {
        "pdf_name": "RP-008307-DS-2-pico-datasheet.pdf",
        "category": "Raspberry_Pi",
        "md_path": "data/processed/raspberry_pi/RP-008307-DS-2-pico-datasheet.md",
        "json_path": "data/metadata/raspberry_pi/RP-008307-DS-2-pico-datasheet.json"
    },
    {
        "pdf_name": "RP-008371-DS-1-rp2040-datasheet.pdf",
        "category": "Raspberry_Pi",
        "md_path": "data/processed/raspberry_pi/RP-008371-DS-1-rp2040-datasheet.md",
        "json_path": "data/metadata/raspberry_pi/RP-008371-DS-1-rp2040-datasheet.json"
    },
    {
        "pdf_name": "RP-009085-KB-2-raspberry-pi-pico-c-sdk.pdf",
        "category": "Raspberry_Pi",
        "md_path": "data/processed/raspberry_pi/RP-009085-KB-2-raspberry-pi-pico-c-sdk.md",
        "json_path": "data/metadata/raspberry_pi/RP-009085-KB-2-raspberry-pi-pico-c-sdk.json"
    }
]

def main():
    print("=== INICIO DE INDEXACIÓN VECTORIAL EN CHROMADB ===")
    chunker = SemanticHardwareChunker(chunk_size=800, chunk_overlap=150)
    embedder = EmbeddingService()
    indexer = VectorIndexer(collection_name="microcontrollers_kb")

    initial_count = indexer.collection.count()
    print(f"Colección actual: '{indexer.collection_name}' | Chunks existentes: {initial_count}")

    # Verificar qué archivos ya tienen chunks en ChromaDB
    all_data = indexer.collection.get(include=["metadatas"])
    existing_files = set()
    for m in all_data.get("metadatas", []):
        fn = m.get("file_name")
        if fn:
            existing_files.add(fn)
    print(f"Archivos ya presentes en ChromaDB ({len(existing_files)}): {sorted(list(existing_files))}")

    total_new_chunks = 0
    indexing_summary = []

    for idx, doc_info in enumerate(DOCUMENTS_TO_INDEX, start=1):
        pdf_name = doc_info["pdf_name"]
        cat = doc_info["category"]
        md_file = Path(doc_info["md_path"])
        json_file = Path(doc_info["json_path"])

        if pdf_name in existing_files:
            print(f"\n[{idx}/{len(DOCUMENTS_TO_INDEX)}] Saltando (ya indexado): {pdf_name}")
            continue

        print(f"\n[{idx}/{len(DOCUMENTS_TO_INDEX)}] Procesando: {pdf_name} ({cat})...")

        if not md_file.exists():
            print(f"  [ERROR] No existe archivo MD: {md_file}")
            continue
        if not json_file.exists():
            print(f"  [ERROR] No existe archivo JSON: {json_file}")
            continue

        text_content = md_file.read_text(encoding="utf-8")
        with open(json_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        component_name = metadata.get("component", pdf_name)

        doc_data = {
            "text": text_content,
            "file_name": pdf_name,
            "category": cat,
            "component": component_name,
            "manufacturer": metadata.get("manufacturer", "unknown"),
            "family": metadata.get("family", "unknown"),
            "document_type": metadata.get("type", "Technical Spec"),
            "interfaces": metadata.get("interfaces", []),
            "source_path": metadata.get("source_path", str(md_file))
        }

        # 1. Chunking
        chunks = chunker.split_document(doc_data)
        if not chunks:
            print(f"  [WARNING] No se generaron chunks para {pdf_name}")
            continue

        print(f"  Chunks generados: {len(chunks)}")

        # 2. Embeddings con reintento ante 429
        texts_to_embed = [c["text"] for c in chunks]
        embeddings = None
        for attempt in range(1, 6):
            try:
                t0 = time.time()
                embeddings = embedder.embed_documents(texts_to_embed)
                t_embed = time.time() - t0
                print(f"  Embeddings calculados en {t_embed:.2f}s ({len(embeddings)} vectores dim {len(embeddings[0])})")
                break
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    print(f"  [QUOTA 429] Límite por minuto alcanzado. Esperando 60 segundos (intento {attempt}/5)...")
                    time.sleep(60)
                else:
                    print(f"  [ERROR INESPERADO]: {err_msg}")
                    raise

        if not embeddings:
            print(f"  [ERROR] No se pudieron generar embeddings para {pdf_name}")
            continue

        # 3. Indexación en ChromaDB
        indexer.index_documents(chunks, embeddings)
        print(f"  Chunks indexados en ChromaDB con éxito.")

        total_new_chunks += len(chunks)
        indexing_summary.append({
            "file_name": pdf_name,
            "category": cat,
            "component": component_name,
            "chunks_count": len(chunks)
        })

        # Pausa suave de 8 segundos entre documentos para ritmo controlado de peticiones
        time.sleep(8.0)

    final_count = indexer.collection.count()
    print("\n" + "=" * 50)
    print("=== RESUMEN DE INDEXACIÓN COMPLETADA ===")
    print(f"Chunks previos: {initial_count}")
    print(f"Nuevos chunks añadidos en esta sesión: {total_new_chunks}")
    print(f"Total en ChromaDB ('microcontrollers_kb'): {final_count}")
    print("Detalle de documentos procesados en esta corrida:")
    for s in indexing_summary:
        print(f"  - {s['file_name']}: {s['chunks_count']} chunks [{s['category']} | {s['component']}]")

    # Guardar resumen en storage
    summary_file = Path("storage/last_embedding_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.time(),
            "total_new_chunks_session": total_new_chunks,
            "final_chroma_count": final_count,
            "new_documents": indexing_summary
        }, f, indent=2, ensure_ascii=False)
    print(f"\nResumen actualizado en: {summary_file}")

if __name__ == "__main__":
    main()
