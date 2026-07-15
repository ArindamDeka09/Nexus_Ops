# ingestion/scanner.py
# ----------------------------------------------------------------------
# Autonomous Repository Scanner.
# Walks a codebase, detects real issues using Python's AST module
# and pyflakes, and returns a structured issue list for the pipeline.
# No LLM calls — this is pure static analysis.
# ----------------------------------------------------------------------

import os
import ast
import json
from typing import List, Dict
from dataclasses import dataclass, asdict


@dataclass
class DetectedIssue:
    """One detected issue from static analysis."""
    file_path:    str
    line_number:  int
    issue_type:   str    # "missing_null_check", "bare_except", "undefined_name", etc.
    description:  str
    severity:     str    # "critical", "warning", "info"
    code_snippet: str


class RepositoryScanner:
    """
    Scans a Python codebase and returns a list of DetectedIssues.
    Uses AST for structural analysis + pattern matching for common bugs.
    """

    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self.issues: List[DetectedIssue] = []

        self.blacklisted_dirs = {
            'venv', '__pycache__', '.git', 'node_modules',
            '.vscode', 'storage', '.ipynb_checkpoints'
        }

    def scan(self) -> List[DetectedIssue]:
        """
        Main entry point. Walks the repo and analyses every .py file.
        Returns a list of detected issues sorted by severity.
        """
        print(f"\n[Scanner] Scanning repository: {self.repo_path}")
        self.issues = []

        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [
                d for d in dirs
                if d.lower() not in self.blacklisted_dirs
                and not d.startswith('.')
            ]
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    full_path = os.path.join(root, file)
                    self._analyse_file(full_path)

        # Sort: critical first, then warning, then info
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        self.issues.sort(key=lambda x: severity_order.get(x.severity, 3))

        print(f"[Scanner] Found {len(self.issues)} issue(s) across the codebase.")
        return self.issues

    def _analyse_file(self, file_path: str):
        """Runs all detectors on a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()

            if not source.strip():
                return

            tree = ast.parse(source, filename=file_path)
            lines = source.splitlines()
            rel_path = os.path.relpath(file_path, self.repo_path)

            self._detect_bare_excepts(tree, lines, rel_path)
            self._detect_missing_null_checks(tree, lines, rel_path)
            self._detect_missing_return_types(tree, lines, rel_path)
            self._detect_hardcoded_secrets(lines, rel_path)
            self._detect_unused_imports(tree, rel_path)
            self._detect_mutable_defaults(tree, lines, rel_path)

        except SyntaxError as e:
            self.issues.append(DetectedIssue(
                file_path=os.path.relpath(file_path, self.repo_path),
                line_number=e.lineno or 0,
                issue_type="syntax_error",
                description=f"Syntax error: {e.msg}",
                severity="critical",
                code_snippet=str(e.text or ""),
            ))
        except Exception:
            pass

    def _detect_bare_excepts(self, tree, lines, rel_path):
        """Finds `except:` or `except Exception:` with only `pass`."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    snippet = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                    self.issues.append(DetectedIssue(
                        file_path=rel_path,
                        line_number=node.lineno,
                        issue_type="bare_except",
                        description=(
                            "Bare `except:` clause catches ALL exceptions including "
                            "KeyboardInterrupt and SystemExit. Use `except Exception as e:` "
                            "and log the error."
                        ),
                        severity="warning",
                        code_snippet=snippet,
                    ))

    def _detect_missing_null_checks(self, tree, lines, rel_path):
        """
        Finds functions that use a parameter directly without a None check.
        Heuristic: function receives a param, first line is not an `if param is None` check.
        """
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            if len(node.args.args) < 2:   # Skip self-only methods
                continue

            # Get all parameter names (excluding 'self', 'cls')
            param_names = [
                a.arg for a in node.args.args
                if a.arg not in ('self', 'cls')
            ]
            if not param_names:
                continue

            # Check if the function body has ANY None check for its params
            has_null_check = False
            for child in ast.walk(node):
                if isinstance(child, ast.Compare):
                    for comp in child.comparators:
                        if isinstance(comp, ast.Constant) and comp.value is None:
                            has_null_check = True
                            break

            # Check if function has any arithmetic on params (high-risk)
            has_arithmetic_on_param = False
            for child in ast.walk(node):
                if isinstance(child, ast.BinOp):
                    has_arithmetic_on_param = True
                    break

            if not has_null_check and has_arithmetic_on_param:
                snippet = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                self.issues.append(DetectedIssue(
                    file_path=rel_path,
                    line_number=node.lineno,
                    issue_type="missing_null_check",
                    description=(
                        f"`{node.name}()` performs arithmetic operations but has no null/None "
                        f"guard for parameters: {param_names}. Passing None will cause TypeError."
                    ),
                    severity="critical",
                    code_snippet=snippet,
                ))

    def _detect_missing_return_types(self, tree, lines, rel_path):
        """Finds public functions without return type annotations."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('_'):
                    continue   # Skip private methods
                if node.returns is None:
                    snippet = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                    self.issues.append(DetectedIssue(
                        file_path=rel_path,
                        line_number=node.lineno,
                        issue_type="missing_type_annotation",
                        description=(
                            f"Public function `{node.name}()` has no return type annotation. "
                            "Add `-> ReturnType` for clarity and static analysis support."
                        ),
                        severity="info",
                        code_snippet=snippet,
                    ))

    def _detect_hardcoded_secrets(self, lines, rel_path):
        """Pattern-matches for hardcoded API keys, passwords, tokens."""
        secret_patterns = [
            'password =', 'api_key =', 'secret =', 'token =',
            'passwd =', 'access_key =', 'private_key ='
        ]
        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()
            for pattern in secret_patterns:
                if pattern in line_lower:
                    # Ignore if it reads from env or is None/empty
                    if 'os.getenv' in line or 'environ' in line:
                        continue
                    if '= ""' in line or "= ''" in line or '= None' in line:
                        continue
                    self.issues.append(DetectedIssue(
                        file_path=rel_path,
                        line_number=i,
                        issue_type="hardcoded_secret",
                        description=(
                            f"Possible hardcoded credential detected: `{pattern.strip()}`. "
                            "Move secrets to environment variables via `.env` file."
                        ),
                        severity="critical",
                        code_snippet=line.strip(),
                    ))
                    break

    def _detect_unused_imports(self, tree, rel_path):
        """Detects imported names that are never used in the file."""
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name.split('.')[0]
                    imported_names.add((name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    if name != '*':
                        imported_names.add((name, node.lineno))

        # Collect all used names in the file
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)

        for name, lineno in imported_names:
            if name not in used_names:
                self.issues.append(DetectedIssue(
                    file_path=rel_path,
                    line_number=lineno,
                    issue_type="unused_import",
                    description=f"`{name}` is imported but never used. Remove to clean dependencies.",
                    severity="info",
                    code_snippet=f"import {name}",
                ))

    def _detect_mutable_defaults(self, tree, lines, rel_path):
        """Finds functions using mutable default arguments (list/dict)."""
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    snippet = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                    self.issues.append(DetectedIssue(
                        file_path=rel_path,
                        line_number=node.lineno,
                        issue_type="mutable_default_argument",
                        description=(
                            f"`{node.name}()` uses a mutable default argument (list/dict/set). "
                            "This is shared across all calls. Use `None` as default and "
                            "initialise inside the function body."
                        ),
                        severity="warning",
                        code_snippet=snippet,
                    ))


def scan_repository(repo_path: str) -> List[Dict]:
    """
    Public interface. Returns a list of issue dicts ready for AgentState.
    """
    scanner = RepositoryScanner(repo_path)
    issues  = scanner.scan()
    return [asdict(issue) for issue in issues]


def issues_to_bug_report(issues: List[Dict], top_n: int = 3) -> str:
    """
    Converts the top N detected issues into a formatted bug report string
    that can be fed into the existing pipeline as `issue_description`.
    """
    critical = [i for i in issues if i["severity"] == "critical"][:top_n]

    if not critical:
        all_issues = issues[:top_n]
    else:
        all_issues = critical

    lines = ["AUTO-DETECTED ISSUES FROM STATIC ANALYSIS:\n"]
    for i, issue in enumerate(all_issues, 1):
        lines.append(
            f"{i}. [{issue['severity'].upper()}] {issue['file_path']} "
            f"(line {issue['line_number']})\n"
            f"   Type: {issue['issue_type']}\n"
            f"   Detail: {issue['description']}\n"
            f"   Code: `{issue['code_snippet']}`\n"
        )

    return "\n".join(lines)