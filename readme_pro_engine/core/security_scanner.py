import re
import os

class SecretScanner:
    def __init__(self):
        # 🔍 Common patterns for leaked secrets
        self.patterns = {
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "GitHub Personal Access Token": r"ghp_[a-zA-Z0-9]{36}",
            "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
            "Generic Password/Secret": r"(?i)(password|secret|passwd|api_key|auth_token)\s*[:=]\s*['\"][0-9a-zA-Z]{8,}['\"]",
            "Firebase Config": r"apiKey:\s*['\"].*['\"]",
        }
        # 📂 Files to ignore (e.g., binaries, images)
        self.ignore_exts = ('.png', '.jpg', '.jpeg', '.gif', '.exe', '.pyc', '.pdf')

    def scan(self, repo_path):
        findings = []
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                # 1. Check for sensitive files (e.g., .env)
                if file.endswith(".env") or file == "config.json" or file == "credentials.json":
                    findings.append(f"⚠️ Sensitive file exposed: `{file}`")
                
                # 2. Scan inside text files for patterns
                if not file.endswith(self.ignore_exts):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for name, pattern in self.patterns.items():
                                if re.search(pattern, content):
                                    findings.append(f"🚨 Potential {name} found in `{relative_path}`")
                    except Exception as e:
                        continue
        return findings