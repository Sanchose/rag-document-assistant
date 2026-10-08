import sys
from pathlib import Path

from src.pipeline import RAGPipeline

pipeline = RAGPipeline()
files = list(Path("data").glob("*.pdf")) + list(Path("data").glob("*.txt"))
print(f"Indexed {pipeline.ingest(files)} chunks from {len(files)} files")

while True:
    q = input("\nFrage / Question (q = quit): ").strip()
    if q.lower() == "q":
        sys.exit()
    result = pipeline.ask(q)
    print("\n" + result["answer"])
    for s in result["sources"]:
        print(f"  - {s['source']}, p.{s['page']} (dist={s['distance']:.2f})")
