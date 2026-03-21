import os
import sys
import re # 👈 Patterns dhoondne ke liye

# Config imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import IGNORE_DIRS, SUPPORTED_EXTENSIONS, TECH_STACK_FILES

class RepositoryScanner:
    def __init__(self, root_path):
        self.root_path = os.path.abspath(root_path) #

    def extract_metadata(self, file_path):
        """
        File ke andar ghus kar signatures (functions/classes) nikalta hai.
        Poori file read nahi karega (memory bachane ke liye), sirf top 150 lines.
        """
        signatures = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.readlines()[:150] 
                for line in content:
                    line = line.strip()
                    # Python, JS, TS, Java ke common patterns
                    if line.startswith(("class ", "def ", "async def ", "export const ", "public class ", "private void ")):
                        # Clean signature (e.g., 'def process_data(res):' -> 'process_data')
                        clean_sig = re.sub(r'\(.*', '', line).replace('class ', '').replace('def ', '').replace('async ', '').strip()
                        signatures.append(clean_sig)
        except Exception as e:
            print(f"⚠️ Metadata extraction failed for {file_path}: {e}")
        return signatures

    def generate_tree(self):
        """AI ko folder structure samajhne ke liye ek visual tree deta hai."""
        tree = []
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS] #
            level = root.replace(self.root_path, '').count(os.sep)
            indent = ' ' * 4 * level
            tree.append(f"{indent}{os.path.basename(root)}/")
            for f in files:
                tree.append(f"{indent}    {f}")
        return "\n".join(tree)

    def scan(self):
        """
        Deep Scan logic:
        1. Config files (pom.xml, package.json)
        2. Code files with internal signatures (Deep Intelligence)
        3. Visual Tree
        """
        results = {
            "config_files": [],
            "code_modules": [],
            "directory_tree": self.generate_tree()
        }

        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS] #

            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.root_path) #

                # 1. Tech Stack Files
                if file in TECH_STACK_FILES: #
                    results["config_files"].append({"name": file, "path": rel_path})

                # 2. Deep Code Scan
                file_ext = os.path.splitext(file)[1]
                if file_ext in SUPPORTED_EXTENSIONS: #
                    full_path = os.path.join(root, file)
                    results["code_modules"].append({
                        "name": file,
                        "path": rel_path,
                        "signatures": self.extract_metadata(full_path) # 👈 Deep Scan yahan ho raha hai
                    })

        return results