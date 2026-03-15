import os
import shutil
import stat
from git import Repo

class GitManager:
    def __init__(self, temp_dir="temp_repo"):
        self.temp_dir = temp_dir

    def _on_rm_error(self, func, path, exc_info):
        """
        Windows Read-Only files handling logic.
        Agar file delete nahi ho rahi toh permission change karke dobara try karega.
        """
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def clone_repo(self, repo_url):
        if os.path.exists(self.temp_dir):
            print(f"🧹 Cleaning up existing temp folder...")
            # Yahan bhi error handler use kar rahe hain
            shutil.rmtree(self.temp_dir, onerror=self._on_rm_error)
        
        print(f"📥 Cloning repository: {repo_url}...")
        try:
            Repo.clone_from(repo_url, self.temp_dir)
            print("✅ Clone successful.")
            return self.temp_dir
        except Exception as e:
            print(f"❌ Error cloning repo: {e}")
            return None

    def cleanup(self):
        if os.path.exists(self.temp_dir):
            # 'onerror' parameter Windows permission error ko handle karega
            shutil.rmtree(self.temp_dir, onerror=self._on_rm_error)
            print("🧹 Temp folder cleaned up.")