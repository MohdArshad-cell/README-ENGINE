import re
import os

class SecretScanner:
    def __init__(self):
        # 🔍 Expanded patterns for professional-grade scanning
        self.patterns = {
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "GitHub Token": r"ghp_[a-zA-Z0-9]{36}",
            "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
            "Stripe API Key": r"sk_live_[0-9a-zA-Z]{24}",
            "Slack Webhook": r"https://hooks.slack.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+",
            "Private Key": r"-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----",
            "Generic Secret": r"(?i)(api_key|secret|passwd|password|auth_token|access_token)\s*[:=]\s*['\"][0-9a-zA-Z]{12,}['\"]",
            "Firebase Config": r"apiKey:\s*['\"].*['\"]",
        }
        
        # 📂 Performance Fix: In directories ko scan karna matlab waqt ki barbadi
        self.ignore_dirs = {'.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build', '.next'}
        self.ignore_exts = ('.png', '.jpg', '.jpeg', '.gif', '.exe', '.pyc', '.pdf', '.svg', '.ico', '.woff', '.woff2')

    def scan(self, repo_path):
        findings = []
        print(f"🛡️ Security scan initiated for: {repo_path}")

        for root, dirs, files in os.walk(repo_path):
            # 🚀 Speed Optimization: Blocklist directories ko ignore karo
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                # 1. High-Value File Check (Direct hits)
                if file in [".env", "credentials.json", "service-account.json", "id_rsa"]:
                    findings.append(f"⚠️ CRITICAL: Sensitive file exposed: `{file}`")
                    continue # File name hi alert hai, andar scan ki zaroorat nahi

                # 2. Content Scan (Memory-Efficient)
                if not file.endswith(self.ignore_exts):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        # Poori file memory mein load nahi karenge agar bohot badi ho
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            # Sirf pehli 1000 lines scan karo (Secrets usually top par hote hain)
                            # Ya poori file scan karo agar file choti hai
                            content = f.read(1000000) # Max 1MB scan per file
                            
                            for name, pattern in self.patterns.items():
                                if re.search(pattern, content):
                                    findings.append(f"🚨 Potential {name} found in `{rel_path}`")
                    except Exception:
                        continue
        
        return findings