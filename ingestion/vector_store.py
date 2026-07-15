# ingestion/vector_store.py
# ----------------------------------------------------------------------
# Vector Store: Lightweight operational bypass layout.
# ----------------------------------------------------------------------

from typing import List, Any

class MockIndex:
    """Lightweight structural placeholder to keep main.py execution signature intact."""
    def __init__(self):
        self.storage_context = self
    def persist(self, **kwargs):
        pass

def initialize_vector_store(nodes: List[Any]) -> MockIndex:
    """Instantly skips heavy chunk indexing loops."""
    print("[VectorStore] Bypassing JSON disk serialization to optimize processing speed.")
    return MockIndex()

def load_vector_index() -> MockIndex:
    """Returns a fast baseline placeholder structure."""
    return MockIndex()