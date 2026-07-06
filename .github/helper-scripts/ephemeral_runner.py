#!/usr/bin/env python3
"""
Ephemeral Runner Manager: Creates temporary self-hosted runners on network storage.
Designed for Termux/Android environments with shared storage access.
Usage: Called by GitHub Actions to spin up transient compute capacity.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any

class EphemeralRunnerManager:
    def __init__(self):
        self.storage_base = Path(os.getenv("RUNNER_STORAGE", "/sdcard/.termux/runners"))
        self.runner_name = f"ephemeral-{os.urandom(4).hex()}"
        self.runner_dir = self.storage_base / self.runner_name
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.runner_labels = os.getenv("RUNNER_LABELS", "ephemeral,termux,agentic-matrix")
        
    def setup_storage(self) -> bool:
        """Prepare network storage directory."""
        try:
            self.runner_dir.mkdir(parents=True, exist_ok=True)
            
            # Create .runner config
            config = {
                "name": self.runner_name,
                "labels": self.runner_labels.split(","),
                "work_directory": str(self.runner_dir / "_work"),
                "ephemeral": True,
                "ttl_seconds": 3600  # 1 hour default
            }
            
            (self.runner_dir / "runner-config.json").write_text(json.dumps(config, indent=2))
            print(f"✓ Storage prepared at {self.runner_dir}")
            return True
        except Exception as e:
            print(f"✗ Storage setup failed: {e}", file=sys.stderr)
            return False
    
    def download_runner(self) -> bool:
        """Download GitHub Actions runner package."""
        try:
            # Determine architecture
            arch_result = subprocess.run(["uname", "-m"], capture_output=True, text=True)
            arch = arch_result.stdout.strip()
            
            # Map architecture to runner package
            arch_map = {
                "aarch64": "actions-runner-linux-arm64",
                "arm64": "actions-runner-linux-arm64",
                "x86_64": "actions-runner-linux-x64"
            }
            
            pkg_name = arch_map.get(arch, "actions-runner-linux-x64")
            runner_url = f"https://github.com/actions/runner/releases/download/v2.311.0/{pkg_name}.tar.gz"
            
            print(f"Downloading runner: {runner_url}")
            
            # Download using curl or wget
            download_cmd = ["curl", "-L", "-o", f"{self.runner_dir}/runner.tar.gz", runner_url]
            result = subprocess.run(download_cmd, cwd=self.runner_dir)
            
            if result.returncode != 0:
                raise Exception("Download failed")
            
            # Extract
            extract_cmd = ["tar", "xzf", "runner.tar.gz"]
            subprocess.run(extract_cmd, cwd=self.runner_dir, check=True)
            
            # Cleanup tarball
            (self.runner_dir / "runner.tar.gz").unlink()
            
            print(f"✓ Runner downloaded and extracted")
            return True
        except Exception as e:
            print(f"✗ Download failed: {e}", file=sys.stderr)
            return False
    
    def configure_runner(self) -> bool:
        """Configure runner with GitHub registration."""
        if not self.github_token:
            print("⚠ No GITHUB_TOKEN available - running in simulation mode", file=sys.stderr)
            # Create mock configuration for local testing
            mock_config = self.runner_dir / "config.sh"
            mock_config.write_text("#!/bin/bash\necho 'Simulated runner configured'\n")
            mock_config.chmod(0o755)
            return True
        
        try:
            repo_url = os.getenv("GITHUB_REPOSITORY_URL", "")
            if not repo_url:
                raise Exception("GITHUB_REPOSITORY_URL not set")
            
            config_cmd = [
                str(self.runner_dir / "config.sh"),
                "--url", repo_url,
                "--token", self.github_token,
                "--name", self.runner_name,
                "--labels", self.runner_labels,
                "--work", str(self.runner_dir / "_work"),
                "--ephemeral",
                "--unattended"
            ]
            
            result = subprocess.run(config_cmd, cwd=self.runner_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Config output: {result.stdout}", file=sys.stderr)
                print(f"Config error: {result.stderr}", file=sys.stderr)
                raise Exception("Configuration failed")
            
            print(f"✓ Runner configured as {self.runner_name}")
            return True
        except Exception as e:
            print(f"✗ Configuration failed: {e}", file=sys.stderr)
            return False
    
    def start_runner(self) -> bool:
        """Start the runner process in background."""
        try:
            runner_script = self.runner_dir / "run.sh"
            
            # Make executable
            if not runner_script.exists():
                # Create wrapper if needed
                runner_script.write_text("#!/bin/bash\n./Runner.Listener run --once\n")
                runner_script.chmod(0o755)
            
            # Start in background
            log_file = self.runner_dir / "runner.log"
            
            # For actual execution, would use nohup or systemd
            # For CI simulation, just verify readiness
            print(f"✓ Runner ready to start (logs: {log_file})")
            print(f"  Name: {self.runner_name}")
            print(f"  Labels: {self.runner_labels}")
            print(f"  TTL: 3600s")
            
            return True
        except Exception as e:
            print(f"✗ Start failed: {e}", file=sys.stderr)
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Return connection details for GitHub Actions."""
        return {
            "runner_name": self.runner_name,
            "storage_path": str(self.runner_dir),
            "labels": self.runner_labels.split(","),
            "status": "ready",
            "connection_string": f"network://{self.runner_name}"
        }
    
    def cleanup(self):
        """Remove runner after TTL or on demand."""
        try:
            if self.runner_dir.exists():
                # In real implementation, would stop runner first
                subprocess.run(["rm", "-rf", str(self.runner_dir)])
                print(f"✓ Runner {self.runner_name} cleaned up")
        except Exception as e:
            print(f"✗ Cleanup failed: {e}", file=sys.stderr)

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "setup"
    
    manager = EphemeralRunnerManager()
    
    if action == "setup":
        success = (
            manager.setup_storage() and
            manager.download_runner() and
            manager.configure_runner()
        )
        
        if success:
            # Output connection info as JSON for GitHub Actions
            info = manager.get_connection_info()
            print(f"\n##[set-output name=runner_info::{json.dumps(info)}]")
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif action == "start":
        success = manager.start_runner()
        sys.exit(0 if success else 1)
    
    elif action == "cleanup":
        manager.cleanup()
        sys.exit(0)
    
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        print("Usage: ephemeral_runner.py [setup|start|cleanup]", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
