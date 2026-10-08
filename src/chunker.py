from dataclasses import dataclass

from src.loader import Page


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    page: int


class Chunker:
    """Splits text into overlapping chunks, preferring to cut at spaces."""

    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> list[str]:
        text = " ".join(text.split())
        if not text:
            return []

        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            if end < len(text):
                space = text.rfind(" ", start + self.chunk_size // 2, end)
                if space != -1:
                    end = space
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(text):
                break
            start = max(end - self.overlap, start + 1)
        return chunks

    def chunk_pages(self, pages: list[Page]) -> list[Chunk]:
        chunks = []
        for p in pages:
            for i, text in enumerate(self.split_text(p.text)):
                chunks.append(
                    Chunk(
                        id=f"{p.source}-p{p.page}-c{i}",
                        text=text,
                        source=p.source,
                        page=p.page,
                    )
                )
        return chunks