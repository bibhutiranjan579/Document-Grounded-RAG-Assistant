import threading
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

_encoder = None
_encoder_lock = threading.Lock()

def get_encoder():
    global _encoder
    if _encoder is None:
        with _encoder_lock:
            if _encoder is None:
                _encoder = SentenceTransformer(EMBEDDING_MODEL)
    return _encoder
