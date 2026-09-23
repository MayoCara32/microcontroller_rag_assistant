from src.retrieval.dense_retriever import DenseRetriever

retriever = DenseRetriever()
queries = [
    "¿Qué registros configuran el convertidor ADC en el ATmega328P?",
    "¿Cómo funciona el bloque PIO en el microcontrolador RP2040?",
    "¿Qué es el clock stretching en el protocolo I2C según UM10204?",
    "¿Cuál es el rango de voltaje de entrada VCC del TL5001A-Q1?"
]

for q in queries:
    print(f"\nConsulta: {q}")
    results = retriever.retrieve(q, top_k=2)
    for r in results:
        comp = r['metadata'].get('component', 'N/A')
        fn = r['metadata'].get('file_name', 'N/A')
        print(f"  [Score: {r['score']:.4f}] {comp} ({fn}):")
        print(f"    {r['text'][:140]}...")
