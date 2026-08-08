import os
from pathlib import Path
import frontmatter
import pymupdf

TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf"}


def load_document(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".txt":
        return path.read_text(encoding="utf-8")
    if ext in {".md", ".markdown"}:
        post = frontmatter.load(path)
        return post.content
    if ext == ".pdf":
        return _load_pdf(path)
    raise ValueError(f"Unsupported document format: {ext}")


def _load_pdf(path: Path) -> str:
    text = []
    with pymupdf.open(path) as doc:
        for page in doc:
            text.append(page.get_text())
    return "\n\n".join(text)


def list_documents(data_dir: Path):
    for path in sorted(data_dir.iterdir()):
        if path.suffix.lower() in TEXT_EXTENSIONS:
            yield path
