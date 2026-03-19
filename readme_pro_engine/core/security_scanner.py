import re
import os

class SecretScanner:
    def __init__(self):
        # Common patterns for secrets
        self.patterns = {
            "AWS Key": r"AKIA[0-9A-Z]{16}",
            "Generic Secret": r"(?i)secret(_|key|token|auth|pass)?\s*[:=]\s*['\"][0-9a-zA-Z]{16,}['\"]",
            "Firebase URL": r"https://.*\.firebaseio\.com",
            "Environment File": r"\.env$"
        }

    def scan(self, repo_path):
        findings = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                # 1. Check for sensitive files
                if file.endswith(".env") or file == "config.json":
                    findings.append(f"⚠️ Sensitive file found: {file}")
                
                # 2. Check inside files (for keys)
                if file.endswith(('.py', '.js', '.ts', '.java', '.go')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for name, pattern in self.patterns.items():
                                if re.search(pattern, content):
                                    findings.append(f"🚨 Potential {name} in {file}")
                    except:
                        continue
        return findings