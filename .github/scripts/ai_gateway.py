#!/usr/bin/env python3
"""
Universal AI Gateway: Routes context bundles to multiple free-tier AI endpoints.
Supports: OpenRouter, HuggingFace, Nvidia, Github Models, Meta, Qwen, Kimi, etc.
Feature: Auto-sources API keys from ENV, Secrets, or embedded config (if safe).
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List

class AIGateway:
    def __init__(self, context_bundle_path: str):
        self.bundle = json.loads(Path(context_bundle_path).read_text())
        self.session = requests.Session()
        
        # Endpoint configurations
        self.endpoints = {
            "openrouter": {
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "model": "meta-llama/llama-3-70b-instruct",
                "auth_env": "OPENROUTER_API_KEY",
                "payload_template": self._openrouter_payload
            },
            "huggingface": {
                "url": "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct",
                "model": "Qwen2.5-Coder-32B-Instruct",
                "auth_env": "HF_API_KEY",
                "payload_template": self._hf_payload
            },
            "github_models": {
                "url": "https://models.inference.ai.azure.com/chat/completions",
                "model": "gpt-4o",
                "auth_env": "GITHUB_TOKEN",
                "payload_template": self._gh_payload
            },
            "nvidia": {
                "url": "https://integrate.api.nvidia.com/v1/chat/completions",
                "model": "meta/llama3-70b-instruct",
                "auth_env": "NVIDIA_API_KEY",
                "payload_template": self._nvidia_payload
            },
            "qwen": {
                "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                "model": "qwen-max",
                "auth_env": "DASHSCOPE_API_KEY",
                "payload_template": self._qwen_payload
            },
            "kimi": {
                "url": "https://api.moonshot.cn/v1/chat/completions",
                "model": "moonshot-v1-8k",
                "auth_env": "KIMI_API_KEY",
                "payload_template": self._kimi_payload
            }
        }

    def _openrouter_payload(self, messages: List[Dict]) -> Dict:
        return {
            "model": "meta-llama/llama-3-70b-instruct",
            "messages": messages,
            "max_tokens": 4000
        }

    def _hf_payload(self, messages: List[Dict]) -> Dict:
        # HF Inference API often expects simple text prompt or specific chat format
        prompt = "\n".join([m["content"] for m in messages])
        return {"inputs": prompt, "parameters": {"max_new_tokens": 2048}}

    def _gh_payload(self, messages: List[Dict]) -> Dict:
        return {
            "model": "gpt-4o",
            "messages": messages,
            "temperature": 0.2
        }

    def _nvidia_payload(self, messages: List[Dict]) -> Dict:
        return {
            "model": "meta/llama3-70b-instruct",
            "messages": messages,
            "max_tokens": 2048
        }

    def _qwen_payload(self, messages: List[Dict]) -> Dict:
        return {
            "model": "qwen-max",
            "input": {"messages": messages},
            "parameters": {"result_format": "message"}
        }

    def _kimi_payload(self, messages: List[Dict]) -> Dict:
        return {
            "model": "moonshot-v1-8k",
            "messages": messages,
            "max_tokens": 2048
        }

    def get_auth(self, provider: str) -> Optional[str]:
        """Attempt to source API key from Env, then Secrets file, then return None."""
        config = self.endpoints.get(provider)
        if not config: return None
        
        # 1. Try Environment Variable
        key = os.getenv(config["auth_env"])
        if key: return key
        
        # 2. Try .github/secrets.json (gitignored)
        secrets_file = Path(".github/secrets.json")
        if secrets_file.exists():
            secrets = json.loads(secrets_file.read_text())
            return secrets.get(config["auth_env"])
        
        return None

    def build_prompt(self) -> str:
        """Construct a comprehensive code review prompt."""
        changes = self.bundle.get("changes", [])
        critical = self.bundle.get("critical_context", {})
        
        prompt = "You are an expert code reviewer for a complex Agentic Matrix Monorepo.\n\n"
        prompt += "## CRITICAL CONTEXT (Read First)\n"
        for path, content in list(critical.items())[:3]: # Limit critical files
            prompt += f"### {path}\n{content[:1000]}...\n\n"
        
        prompt += "## CHANGES TO REVIEW\n"
        for change in changes:
            prompt += f"### File: {change['path']}\n"
            prompt += f"DIFF:\n{change['diff']}\n"
            if "content" in change:
                prompt += f"FULL CONTENT:\n{change['content'][:2000]}...\n"
            prompt += "\n"
        
        prompt += "## TASK\n1. Analyze correctness, security, and architecture.\n2. Check for 'drift' against the critical context.\n3. Suggest improvements.\n4. Output JSON: { 'verdict': 'PASS/FAIL', 'issues': [], 'score': 0-10 }"
        
        return prompt

    def call_provider(self, provider: str) -> Dict[str, Any]:
        """Execute request to specific provider."""
        auth = self.get_auth(provider)
        if not auth:
            return {"error": f"No API key found for {provider}", "status": "skipped"}
        
        config = self.endpoints[provider]
        headers = {
            "Authorization": f"Bearer {auth}",
            "Content-Type": "application/json"
        }
        
        # Special headers for some providers
        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/local-repo"
            headers["X-Title"] = "CI Code Review"
        elif provider == "github_models":
            headers["Accept"] = "application/vnd.github+json"

        prompt = self.build_prompt()
        messages = [{"role": "user", "content": prompt}]
        
        payload = config["payload_template"](messages)
        
        try:
            response = self.session.post(config["url"], headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def run_all(self, target_provider: Optional[str] = None) -> Dict[str, Any]:
        results = {}
        providers_to_run = [target_provider] if target_provider else self.endpoints.keys()
        
        for provider in providers_to_run:
            if provider not in self.endpoints:
                print(f"Warning: Unknown provider {provider}")
                continue
            print(f"Calling {provider}...")
            results[provider] = self.call_provider(provider)
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Gateway for Code Review')
    parser.add_argument('bundle_path', nargs='?', default='.github/context-bundle.json', help='Path to context bundle')
    parser.add_argument('--provider', type=str, help='Specific provider to call (optional)')
    args = parser.parse_args()
    
    gateway = AIGateway(args.bundle_path)
    results = gateway.run_all(target_provider=args.provider)
    
    output_file = Path(".github/ai-reviews.json")
    output_file.write_text(json.dumps(results, indent=2))
    print(f"Reviews saved to {output_file.resolve()}")
    print(json.dumps({k: v.get("status") for k, v in results.items()}))
