import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


def clean_text(text: str) -> str:
    # remove stray control characters (e.g. \x88)
    text = re.sub(r"[\x80-\x9f]", "", text)
    # fix detached umlaut accents: "¨u" -> "ü"
    umlauts = {"a": "ä", "o": "ö", "u": "ü", "A": "Ä", "O": "Ö", "U": "Ü"}
    text = re.sub(r"¨\s*([aouAOU])", lambda m: umlauts[m.group(1)], text)
    # remove the space before the fixed letter: "sp ätestens" -> "spätestens"
    text = re.sub(r"(?<=\w) (?=[äöüÄÖÜ])", "", text)
    return text


@dataclass
class Page:
    text: str
    source: str  # file name
    page: int    # page number (from 1)


class DocumentLoader:
    """Reads PDF and TXT files and returns text page by page."""

    SUPPORTED = {".pdf", ".txt"}

    def load(self, path: str | Path) -> list[Page]:
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._load_pdf(path)
        if suffix == ".txt":
            return self._load_txt(path)
        raise ValueError(f"Unsupported file type: {suffix}")

    def _load_pdf(self, path: Path) -> list[Page]:
        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = clean_text(page.extract_text() or "").strip()
            if text:
                pages.append(Page(text=text, source=path.name, page=i))
        return pages

    def _load_txt(self, path: Path) -> list[Page]:
        text = clean_text(path.read_text(encoding="utf-8")).strip()
        return [Page(text=text, source=path.name, page=1)] if text else []