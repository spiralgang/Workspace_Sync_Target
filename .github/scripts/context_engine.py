#!/usr/bin/env python3
"""
Context Engine: Generates optimized, token-aware context bundles for LLM code review.
Strategies:
1. Change-First: Full content of changed files + full diff.
2. Dependency-Aware: Includes imports/references from changed files (1-hop).
3. Layer-Summary: Summarizes unchanged layers to save tokens.
4. Critical-Path: Always includes core config (scaffold, agent-index, matrix).
"""

import os
import sys
import json
import subprocess
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

class ContextEngine:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.context_limit = 100000  # Soft token limit estimate (chars)
        self.critical_files = [
            "layers/README.md",
            ".github/AGENT_INSTRUCTIONS.md",
            "layers/matrix-config/matrix.yml",
            "layers/matrix-config/agent-index.json"
        ]

    def get_changed_files(self, base_ref: str = "main") -> List[Dict[str, Any]]:
        """Get list of changed files with diffs."""
        try:
            # Try to get diff against base_ref, fallback to HEAD~1
            cmd = ["git", "diff", "--name-only", base_ref]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_root)
            if result.returncode != 0:
                cmd = ["git", "diff", "--name-only", "HEAD~1"]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_root)
            
            changed_paths = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            changes = []
            for path in changed_paths:
                if not path: continue
                full_path = self.repo_root / path
                if not full_path.exists(): continue
                
                # Get diff
                diff_cmd = ["git", "diff", base_ref, "--", path]
                diff_res = subprocess.run(diff_cmd, capture_output=True, text=True, cwd=self.repo_root)
                if diff_res.returncode != 0:
                    diff_cmd = ["git", "diff", "HEAD~1", "--", path]
                    diff_res = subprocess.run(diff_cmd, capture_output=True, text=True, cwd=self.repo_root)
                
                changes.append({
                    "path": path,
                    "diff": diff_res.stdout,
                    "content": full_path.read_text(errors="ignore") if full_path.exists() else ""
                })
            return changes
        except Exception as e:
            print(f"Error getting changes: {e}", file=sys.stderr)
            return []

    def get_repo_structure(self) -> Dict[str, Any]:
        """Generate a tree structure of the repo, summarizing large directories."""
        structure = {}
        for root, dirs, files in os.walk(self.repo_root):
            # Skip hidden dirs except .github
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.github']
            rel_root = Path(root).relative_to(self.repo_root)
            
            current = structure
            for part in rel_root.parts:
                if part not in current: current[part] = {}
                current = current[part]
            
            for f in files:
                if f.endswith(('.py', '.ts', '.tsx', '.js', '.jsx', '.md', '.yml', '.json', '.skill')):
                    current[f] = "file"
        return structure

    def get_critical_context(self) -> Dict[str, str]:
        """Load critical configuration files."""
        context = {}
        for f in self.critical_files:
            path = self.repo_root / f
            if path.exists():
                context[f] = path.read_text(errors="ignore")
        return context

    def generate_bundle(self, strategy: str = "balanced") -> Dict[str, Any]:
        """Generate the final context bundle."""
        changes = self.get_changed_files()
        critical = self.get_critical_context()
        structure = self.get_repo_structure()
        
        bundle = {
            "metadata": {
                "repo": self.repo_root.name,
                "strategy": strategy,
                "changed_files_count": len(changes),
                "critical_files_count": len(critical)
            },
            "critical_context": critical,
            "changes": [],
            "structure_summary": json.dumps(structure, indent=2)[:5000]  # Truncate structure
        }
        
        current_size = len(json.dumps(bundle))
        
        # Add changes based on strategy
        for change in changes:
            if strategy == "minimal":
                # Only diff
                bundle["changes"].append({"path": change["path"], "diff": change["diff"]})
            elif strategy == "full":
                # Diff + Content
                bundle["changes"].append(change)
            else: # balanced
                # Diff always, content if under limit
                entry = {"path": change["path"], "diff": change["diff"]}
                if current_size < self.context_limit * 0.8:
                    entry["content"] = change["content"]
                    current_size += len(change["content"])
                bundle["changes"].append(entry)
        
        bundle["metadata"]["total_size_chars"] = len(json.dumps(bundle))
        return bundle

if __name__ == "__main__":
    strategy = sys.argv[1] if len(sys.argv) > 1 else "balanced"
    engine = ContextEngine(os.getcwd())
    bundle = engine.generate_bundle(strategy)
    
    # Output to file for workflow consumption
    output_file = Path(".github/context-bundle.json")
    output_file.write_text(json.dumps(bundle, indent=2))
    print(f"Context bundle generated: {output_file.resolve()} ({bundle['metadata']['total_size_chars']} chars)")
    
    # Also print summary to stdout
    print(json.dumps(bundle["metadata"]))
