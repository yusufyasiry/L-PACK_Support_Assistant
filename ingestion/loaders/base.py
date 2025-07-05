# base.py
from abc import ABC, abstractmethod
from typing import List, Dict
from langchain_core.documents import Document
import pathlib, hashlib

class BaseLoader(ABC):
    """All concrete loaders inherit from this so you get a unified API."""

    @abstractmethod
    def load(self) -> List[Document]:
        pass

    # ── helpers you'll re-use ────────────────────────────────────────────
    def _make_id(self, source: str, extra: str | None = None) -> str:
        h = hashlib.sha256((source + (extra or "")).encode()).hexdigest()
        return h[:32]                     # 32-char deterministic id

    def _abspath(self, path: str | pathlib.Path) -> str:
        return str(pathlib.Path(path).expanduser().resolve())
