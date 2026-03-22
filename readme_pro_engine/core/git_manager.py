import os
import shutil
import stat
import uuid # 👈 Ye missing tha!
from git import Repo

class GitManager:
    def __init__(self, temp_dir=None):
        """
        🛠️ Unique Folder Logic: 
        Agar temp_dir nahi di jati, toh UUID folder banega. 
        Isse multiple workers aapas mein nahi takrayenge.
        """
        if temp_dir is None:
            # unique ID generator
            self.temp_dir = f"temp_repo_{uuid.uuid4().hex}"
        else:
            self.temp_dir = temp_dir

    def _on_rm_error(self, func, path, exc_info):
        """
        Windows/Linux Read-Only files fix.
        .git folder ke andar ki files kabhi-kabhi delete nahi hoti, ye use force karta hai.
        """
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print(f"⚠️ Cleanup Warning: {path} delete nahi hua: {e}")

    def clone_repo(self, repo_url):
        """
        Clones the repository into a unique temporary directory.
        """
        # Purana kachra saaf karna agar folder exist karta hai
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, onerror=self._on_rm_error)
        
        print(f"📥 Cloning into: {self.temp_dir}")
        try:
            Repo.clone_from(repo_url, self.temp_dir)
            return self.temp_dir
        except Exception as e:
            print(f"❌ Clone Error: {e}")
            return None

    def cleanup(self):
        """
        Processing ke baad folder delete karna mandatory hai varna server bhar jayega.
        """
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, onerror=self._on_rm_error)
            print(f"🧹 Workspace cleaned: {self.temp_dir}")


    # core/git_manager.py mein ye method add karo
def get_diff(self, before_sha, after_sha):
    """Do commits ke beech ka diff nikalta hai."""
    try:
        import subprocess
        # --stat se humein files changed ki list milti hai
        # -U0 se sirf changed lines milti hain (tokens bachane ke liye)
        cmd = ["git", "-C", self.temp_dir, "diff", before_sha, after_sha, "--stat"]
        diff_stat = subprocess.check_output(cmd).decode('utf-8')
        
        cmd_content = ["git", "-C", self.temp_dir, "diff", before_sha, after_sha, "-U0"]
        diff_content = subprocess.check_output(cmd_content).decode('utf-8')
        
        return {
            "stat": diff_stat,
            "content": diff_content[:5000] # Token limit safety
        }
    except Exception as e:
        print(f"❌ Diff extraction failed: {e}")
        return None