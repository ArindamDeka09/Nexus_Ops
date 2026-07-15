# ingestion/document_loader.py
# ----------------------------------------------------------------------
# Document Loader: Crawls directories and extracts source code assets
# into LlamaIndex Document nodes while preserving structural metadata.
# ----------------------------------------------------------------------

import os
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, Document
from typing import List

# Supported language formats mapping for code perception scanning
SUPPORTED_EXTENSIONS = [
    ".py", ".js", ".ts", ".java", ".cpp", ".c",
    ".cs", ".go", ".rs", ".rb", ".php", ".html",
    ".css", ".json", ".yaml", ".yml", ".md", ".txt"
]

def load_codebase(directory: str) -> List[Document]:
    """
    Recursively scans the target directory for supported code files, 
    parses them, and injects file pathing/language tags into the metadata.
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Target repository directory not found: {directory}")

    print(f"[Loader] Starting file scan under: {directory_path.resolve()}")

    valid_files = []
    for root, dirs, files in os.walk(directory_path):
        # Prevent searching through massive environment trees or temporary cache assets
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                   ['__pycache__', 'node_modules', '.git', 'venv', '.venv', 'dist', 'build']]
        
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                valid_files.append(os.path.join(root, file))

    if not valid_files:
        raise ValueError(f"No source code or text assets matched search parameters in: {directory}")

    print(f"[Loader] Discovered {len(valid_files)} valid file entries to ingest.")

    # Utilize core LlamaIndex reader engines to pull file data objects
    reader = SimpleDirectoryReader(input_files=valid_files)
    documents = reader.load_data()

    # Apply relational metadata properties to enrich context processing
    for doc, filepath in zip(documents, valid_files):
        ext = Path(filepath).suffix.lower()
        lang_map = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".java": "Java", ".cpp": "C++", ".c": "C", ".cs": "C#",
            ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP"
        }
        doc.metadata["file_path"] = filepath
        doc.metadata["file_name"] = Path(filepath).name
        doc.metadata["language"] = lang_map.get(ext, "Unknown")

    print(f"[Loader] Successfully generated {len(documents)} context document blobs.")
    return documents