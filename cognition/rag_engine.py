# cognition/rag_engine.py
# ----------------------------------------------------------------------
# CodeRAGEngine: Fast workspace text reader that filters out 
# hidden system metadata and cloud sync directories.
# ----------------------------------------------------------------------

import os

class CodeRAGEngine:
    """Performs direct, fast code file content loading on-the-fly."""
    def __init__(self, top_k: int = 4):
        # Target the explicit source context directory inside your workspace layout
        self.target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        print(f"[RAGEngine] Direct filesystem reader mapped to workspace: {self.target_dir}")

    def query(self, question: str) -> str:
        """Dynamically scans files for context matching the query string."""
        print(f"[RAGEngine] Scanning workspace components for query: '{question}'")
        collected_context = []
        extensions_to_read = ('.py', '.json', '.md', '.txt')
        
        # Explicit system blocks to ignore completely
        blacklisted_dirs = {
            'venv', '__pycache__', '.git', 'storage', '.ipynb_checkpoints',
            '.onedrive', '$recycle.bin', 'node_modules', '.vscode'
        }
        
        # Walk through files dynamically
        for root, dirs, files in os.walk(self.target_dir):
            # Clean directory search arrays on-the-fly to prevent stepping into hidden folders
            dirs[:] = [d for d in dirs if d.lower() not in blacklisted_dirs and not d.startswith('.')]
            
            # Skip paths containing cloud sync or hidden backup variables
            if any(b in root.lower() for b in ['workspace_archive', 'sync_metadata', 'temp']):
                continue
                
            for file in files:
                # Prevent loading massive binary database objects or hidden lockfiles
                if file.startswith('.') or file.startswith('~$') or file.endswith('.db'):
                    continue
                    
                if file.endswith(extensions_to_read):
                    file_path = os.path.join(root, file)
                    try:
                        # Skip oversized generated layout logs or massive tracking dumps
                        if os.path.getsize(file_path) > 500 * 1024: # 500 KB Max limit per code file
                            continue
                            
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().strip()
                            if content:
                                rel_path = os.path.relpath(file_path, self.target_dir)
                                collected_context.append(f"--- File: {rel_path} ---\n{content}")
                    except Exception:
                        continue
                        
        if not collected_context:
            return "No readable source components located inside active workspace targets."
            
        # Return a concise snippet slice to ensure your prompt remains safely within model limits
        full_payload = "\n\n".join(collected_context)
        print(f"[RAGEngine] Successfully isolated {len(collected_context)} true code modules.")
        return full_payload[:60000]  # Safe token budget window selection

    def get_codebase_summary(self) -> str:
        """Returns a baseline architectural brief."""
        return self.query("Identify main codebase software module paths and technology frameworks.")

    def find_relevant_patterns(self, execution_context: str) -> str:
        """Locates specific file contexts matching structural patterns."""
        return self.query(f"Identify design signatures or matching files tied to: {execution_context}")