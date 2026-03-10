import os
import sys

# Hum config ko import kar rahe hain. 
# Kyuki scanner.py 'core' folder ke andar hai, hume path handle karna padega.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import IGNORE_DIRS, SUPPORTED_EXTENSIONS, TECH_STACK_FILES

class RepositoryScanner:
    def __init__(self, root_path):
        self.root_path = os.path.abspath(root_path)

    def scan(self):
        """
        Repo ko scan karta hai aur do lists return karta hai:
        1. config_files: Tech stack pehchanne ke liye (pom.xml, etc.)
        2. code_files: Logic analyze karne ke liye (.java, .py, etc.)
        """
        filtered_files = {
            "config_files": [],
            "code_files": []
        }

        for root, dirs, files in os.walk(self.root_path):
            # 1. Junk folders ko modify kar rahe hain taaki os.walk unme na ghuse
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                # File ka relative path nikal rahe hain (AI ko dikhane ke liye)
                rel_path = os.path.relpath(os.path.join(root, file), self.root_path)

                # 2. Check agar ye koi Tech Stack/Config file hai
                if file in TECH_STACK_FILES:
                    filtered_files["config_files"].append({
                        "name": file,
                        "path": rel_path
                    })

                # 3. Check agar ye koi Supported Code file hai
                file_ext = os.path.splitext(file)[1]
                if file_ext in SUPPORTED_EXTENSIONS:
                    filtered_files["code_files"].append({
                        "name": file,
                        "path": rel_path,
                        "extension": file_ext
                    })

        return filtered_files

# Testing logic (sirf dekhne ke liye ki kaam kar raha hai ya nahi)
if __name__ == "__main__":
    # Yahan apne kisi bhi project ka path daal kar test kar sakte ho
    test_path = "." 
    scanner = RepositoryScanner(test_path)
    results = scanner.scan()
    print(f"Found {len(results['config_files'])} Config files.")
    print(f"Found {len(results['code_files'])} Code files.")