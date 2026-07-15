# ingestion/code_splitter.py
# ----------------------------------------------------------------------
# Code Splitter: Splits source documents into manageable chunks
# semantically optimized using token-count chunk configurations.
# ----------------------------------------------------------------------

from llama_index.core import Document
from llama_index.core.node_parser import TokenTextSplitter
from typing import List

def split_documents(documents: List[Document], chunk_size: int = 600, chunk_overlap: int = 60) -> List:
    """
    Takes enriched Document structures from the loader and uses token-based
    chunk splitting to cut files into clean segments without tree-sitter errors.
    """
    print(f"[Splitter] Initializing token parser for {len(documents)} documents...")
    
    # Using TokenTextSplitter ensures perfect cross-platform compilation
    splitter = TokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Process documents down to node text fragments
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"[Splitter] Processing complete! Generated {len(nodes)} logic chunks.")
    return nodes