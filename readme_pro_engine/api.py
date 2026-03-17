import os
import requests
import time
import httpx
import base64
import uvicorn
import hmac
import hashlib
import jwt
import uuid
import shutil
import stat
from fastapi import BackgroundTasks, Header, Request
from datetime import datetime, timedelta
from google import genai
from fastapi import FastAPI, HTTPException, Request , BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from git import Repo
# 🛠️ Core Engine Imports
from core.git_manager import GitManager
from core.scanner import RepositoryScanner
from core.analyzer import ProjectAnalyzer
from core.report_builder import ReportBuilder
from core.cache_manager import cache_mgr
# .env file load karo
load_dotenv()

app = FastAPI(title="README_ENGINE_FINAL_V2", version="2.0")

# api.py mein purane CORSMiddleware ko hata kar ye dalo


# Origins ki list
origins = [
    "https://readme-engine.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], # Explicitly add OPTIONS
    allow_headers=["*"],
    expose_headers=["*"],
)
# 🧠 Gemini & GitHub Config
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = "gemini-2.5-flash-lite"

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

class RepoRequest(BaseModel):
    url: str

@app.get("/")
async def health_check():
    return {"status": "online", "engine": "ENGINE_v2", "cache": "enabled" if cache_mgr.client else "disabled"}



# ... (baaki imports same rahenge)

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")


class GitManager:
    def __init__(self, temp_dir=None):
        """
        🛠️ Unique Folder Logic: 
        Agar temp_dir nahi di jati, toh ye automatic ek unique UUID folder banayega.
        Isse 'Race Condition' khatam ho jati hai.
        """
        if temp_dir is None:
            self.temp_dir = f"temp_repo_{uuid.uuid4().hex}"
        else:
            self.temp_dir = temp_dir

    def _on_rm_error(self, func, path, exc_info):
        """
        Windows Read-Only files handling logic.
        Agar file delete nahi ho rahi toh permission change karke dobara try karega.
        """
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print(f"⚠️ Could not remove {path}: {e}")

    def clone_repo(self, repo_url):
        """
        Clones the repository into a unique temporary directory.
        """
        # Safety Check: Wese toh UUID unique hota hai, par redundancy ke liye
        if os.path.exists(self.temp_dir):
            print(f"🧹 Cleaning up existing folder: {self.temp_dir}")
            shutil.rmtree(self.temp_dir, onerror=self._on_rm_error)
        
        print(f"📥 Cloning repository into: {self.temp_dir}...")
        try:
            # Repository ko clone karna
            Repo.clone_from(repo_url, self.temp_dir)
            print(f"✅ Clone successful in {self.temp_dir}")
            return self.temp_dir
        except Exception as e:
            print(f"❌ Error cloning repo: {e}")
            return None

    def cleanup(self):
        """
        Deletes the unique temporary directory after processing is done.
        """
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, onerror=self._on_rm_error)
            print(f"🧹 Temp folder {self.temp_dir} cleaned up.")


# 🛠️ UTILITY: Signature Verification (Security for Business)
def verify_signature(payload_body: bytes, signature_header: str):
    if not WEBHOOK_SECRET:
        return True # Testing ke liye
    hash_object = hmac.new(WEBHOOK_SECRET.encode(), payload_body, hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

# ---------------------------------------------------------
# 🤖 THE BACKGROUND WORKER (The "Ghost" in the Machine)
# ---------------------------------------------------------
async def process_webhook_task(repo_url: str, branch: str, installation_id: int):
    print(f"🤖 Universal Bot started for: {repo_url} (ID: {installation_id})")
    
    # 1. Get a Fresh Installation Token (The Master Key)
    token = get_installation_token(installation_id)
    if not token:
        print("❌ Could not generate installation token. Aborting.")
        return

    # 2. Authenticated Cloning Logic
    # Universal access ke liye humein token URL mein embed karna padta hai
    # Format: https://x-access-token:<token>@github.com/owner/repo.git
    auth_repo_url = repo_url.replace("https://", f"https://x-access-token:{token}@")
    
    git_mgr = GitManager()
    target_path = git_mgr.clone_repo(auth_repo_url)
    
    if not target_path:
        print(f"❌ Failed to clone {repo_url}")
        return

    try:
        # --- Standard Engine Flow ---
        scanner = RepositoryScanner(target_path)
        data = scanner.scan()
        
        analyzer = ProjectAnalyzer(target_path)
        report = analyzer.analyze(data)
        
        builder = ReportBuilder(target_path)
        final_report = builder.build(data, report)

        # --- Gemini AI Step ---
        prompt = f"Act as a Senior Architect. Update this README with professional diagrams and clear structure: {final_report}"
        gemini_result = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        markdown = gemini_result.text if gemini_result else ""

        if not markdown: 
            print("⚠️ Gemini returned empty text.")
            return

        # --- 🚀 GITHUB ACTION: CREATE PR ---
        parts = repo_url.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
        
        async with httpx.AsyncClient() as http_client:
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            base_url = f"https://api.github.com/repos/{owner}/{repo}"

            # Step A: Get latest SHA of README (if exists)
            content_res = await http_client.get(f"{base_url}/contents/README.md", headers=headers)
            current_sha = content_res.json().get("sha") if content_res.status_code == 200 else None

            # Step B: Create a unique branch
            new_branch = f"readme-ai-update-{int(time.time())}"
            main_ref = await http_client.get(f"{base_url}/git/ref/heads/{branch}", headers=headers)
            main_sha = main_ref.json()["object"]["sha"]

            await http_client.post(f"{base_url}/git/refs", headers=headers, json={
                "ref": f"refs/heads/{new_branch}",
                "sha": main_sha
            })

            # Step C: Commit File
            encoded_content = base64.b64encode(markdown.encode()).decode()
            await http_client.put(f"{base_url}/contents/README.md", headers=headers, json={
                "message": "docs: AI-powered architecture update 🤖",
                "content": encoded_content,
                "branch": new_branch,
                "sha": current_sha
            })

            # Step D: Open PR
            pr_res = await http_client.post(f"{base_url}/pulls", headers=headers, json={
                "title": "📝 AI Documentation Update",
                "body": f"## Why this PR?\nDetected a code push on `{branch}`. I have analyzed the repository and updated the README with the latest architectural changes.\n\n_Generated by **README-ENGINE-PRO**_",
                "head": new_branch,
                "base": branch
            })

            if pr_res.status_code == 201:
                print(f"🎉 SUCCESS! PR opened: {pr_res.json().get('html_url')}")
            else:
                print(f"⚠️ PR Failed: {pr_res.text}")

    except Exception as e:
        print(f"❌ Critical Error in Worker: {e}")
    finally:
        git_mgr.cleanup()

# ---------------------------------------------------------
# 📡 THE WEBHOOK ENDPOINT
# ---------------------------------------------------------
@app.post("/webhook")
async def github_webhook(
    request: Request, 
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None) # 👈 Header yahan capture karo
):
    # 1. Raw bytes lo signature verification ke liye
    payload_bytes = await request.body()
    
    # 2. Signature Verify karo (Security Guard)
    if not verify_signature(payload_bytes, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid Signature")

    # 3. Ab JSON parse karo
    import json
    data = json.loads(payload_bytes)
    
    if "repository" in data and "installation" in data:
        repo_url = data["repository"]["html_url"]
        installation_id = data["installation"]["id"]
        branch = data.get("ref", "refs/heads/main").split("/")[-1]
        
        background_tasks.add_task(process_webhook_task, repo_url, branch, installation_id)
        return {"status": "accepted", "message": "App Engine Waking Up..."}
    
    return {"status": "ignored"}



def get_installation_token(installation_id: int):
    # 1. Load variables
    app_id = os.getenv("GITHUB_APP_ID")
    # 🔥 CRITICAL FIX: Replace literal '\n' with actual newline characters
    private_key = os.getenv("GITHUB_PRIVATE_KEY").replace("\\n", "\n")

    # 2. Create JWT (Proof that WE are the App)
    # JWT expiry 10 mins se zyada nahi honi chahiye
    now = int(time.time())
    payload = {
        "iat": now - 60,           # Issued at (1 min ago for clock drift)
        "exp": now + (10 * 60),    # Expires in 10 mins
        "iss": app_id              # GitHub App ID
    }

    try:
        # RS256 algorithm uses the Private Key to sign the JWT
        encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    except Exception as e:
        print(f"❌ JWT SIGNING FAILED: {e}")
        return None

    # 3. Exchange JWT for an Installation Access Token
    headers = {
        "Authorization": f"Bearer {encoded_jwt}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    
    # Sync request for token exchange (Fast and mandatory before processing)
    with httpx.Client() as client:
        response = client.post(url, headers=headers)
        if response.status_code == 201:
            return response.json().get("token")
        else:
            print(f"❌ TOKEN EXCHANGE FAILED: {response.text}")
            return None
        

# ---------------------------------------------------------
# 🔑 1. GITHUB OAUTH TOKEN EXCHANGE
# ---------------------------------------------------------
@app.post("/github/token")
async def get_github_token(request: dict):
    code = request.get("code")
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://github.com/login/oauth/access_token",
            params={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        return res.json()

# ---------------------------------------------------------
# 📤 2. DIRECT PUSH TO GITHUB
# ---------------------------------------------------------
@app.post("/github/push")
async def push_to_github(request: dict):
    token = request.get("token")
    repo_url = request.get("repo_url") 
    content = request.get("content")
    
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    async with httpx.AsyncClient() as client:
        get_res = await client.get(f"https://api.github.com/repos/{owner}/{repo}/contents/README.md", headers=headers)
        sha = get_res.json().get("sha") if get_res.status_code == 200 else None
        encoded_content = base64.b64encode(content.encode()).decode()

        payload = {"message": "🚀 README updated via ENGINE_v2", "content": encoded_content}
        if sha: payload["sha"] = sha

        put_res = await client.put(f"https://api.github.com/repos/{owner}/{repo}/contents/README.md", headers=headers, json=payload)
        return {"status": "success", "url": put_res.json().get("content", {}).get("html_url")}

# ---------------------------------------------------------
# 🌿 3. CREATE PULL REQUEST (Ensure NO Indentation here!)
# ---------------------------------------------------------
@app.post("/github/pull-request")
async def create_pr(request: dict):
    # 🔍 DEBUG: Print incoming keys to Render logs
    print(f"📥 Received PR Request. Keys: {list(request.keys())}")
    
    token = request.get("token")
    repo_url = request.get("repo_url")
    content = request.get("content")
    
    # 🕵️‍♂️ DETAILED VALIDATION
    missing = []
    if not token: missing.append("token")
    if not repo_url: missing.append("repo_url")
    if not content: missing.append("content")
    
    if missing:
        error_msg = f"❌ ERROR: Missing fields: {', '.join(missing)}"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    # URL parsing
    repo_url = repo_url.rstrip("/")
    parts = repo_url.split("/")
    owner, repo = parts[-2], parts[-1]
    
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    base_api = f"https://api.github.com/repos/{owner}/{repo}"

    async with httpx.AsyncClient() as client:
        try:
            print(f"🚀 Starting PR process for {owner}/{repo}")
            
            # 1. Get Default Branch
            repo_res = await client.get(base_api, headers=headers)
            main_branch = repo_res.json().get("default_branch", "main")
            
            # 2. Get main SHA
            ref_res = await client.get(f"{base_api}/git/ref/heads/{main_branch}", headers=headers)
            main_sha = ref_res.json()["object"]["sha"]

            # 3. Create Unique Branch
            new_branch = f"ai-docs-{int(time.time())}"
            await client.post(f"{base_api}/git/refs", headers=headers, json={
                "ref": f"refs/heads/{new_branch}",
                "sha": main_sha
            })

            # 4. Get README SHA (if exists)
            readme_res = await client.get(f"{base_api}/contents/README.md?ref={new_branch}", headers=headers)
            file_sha = readme_res.json().get("sha") if readme_res.status_code == 200 else None

            # 5. Commit
            encoded_content = base64.b64encode(content.encode()).decode()
            await client.put(f"{base_api}/contents/README.md", headers=headers, json={
                "message": "docs: AI-generated architecture update",
                "content": encoded_content,
                "branch": new_branch,
                "sha": file_sha
            })

            # 6. Create PR
            pr_res = await client.post(f"{base_api}/pulls", headers=headers, json={
                "title": "📝 AI Documentation Update",
                "body": "This PR was generated by ENGINE_v2. Review changes to architecture and README.",
                "head": new_branch,
                "base": main_branch
            })
            
            return {"status": "success", "pr_url": pr_res.json().get("html_url")}

        except Exception as e:
            print(f"❌ PR EXCEPTION: {str(e)}")
            return {"status": "error", "message": str(e)}
        


# ---------------------------------------------------------
# 📊 3. GENERATE MERMAID ARCHITECTURE DIAGRAM
# ---------------------------------------------------------
@app.post("/generate-diagram")
async def generate_diagram(request: dict):
    repo_url = request.get("url")
    if not repo_url:
        raise HTTPException(status_code=400, detail="Repo URL missing")

    git_mgr = GitManager()
    target_path = git_mgr.clone_repo(repo_url)
    
    try:
        scanner = RepositoryScanner(target_path)
        data = scanner.scan()
        analyzer = ProjectAnalyzer(target_path)
        report = analyzer.analyze(data)

        full_context = {
            "stack": report.get("primary_stack"),
            "frameworks": report.get("detected_frameworks"),
            "dependencies": report.get("key_dependencies")[:15],
            "structure": list(data.get("structure", []))[:30]
        }

        # 🎯 PROMPT: Logic clear, constraints tight.
        prompt = f"""
        Generate a simple Mermaid.js 'graph TD' flowchart for this project.
        RULES:
        1. Use only alphanumeric characters and spaces in labels.
        2. Format: A["Label Text"] --> B["Label Text"]
        3. No subgraphs, no classDef, no stylized nodes.
        4. Output ONLY the raw Mermaid code.
        Context: {full_context}
        """

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        raw_code = response.text.replace("```mermaid", "").replace("```", "").strip()

        # 🚀 BASIC CLEANER: Just ensure quotes are balanced and graph TD is there
        import re
        
        # Ensure it starts with graph TD
        if not raw_code.startswith("graph TD"):
            raw_code = "graph TD\n" + raw_code.replace("graph TD", "")

        # Kill any parentheses or slashes that might still leak in
        raw_code = raw_code.replace("(", " ").replace(")", " ").replace("/", " ")
        
        # Simple regex to wrap everything in quotes if AI forgot
        def simple_fix(match):
            return f'{match.group(1)}["{match.group(2).strip()}"]'
        
        raw_code = re.sub(r'(\w+)\[(.*?)\]', simple_fix, raw_code)

        return {
            "status": "success",
            "mermaid_code": raw_code
        }
    finally:
        git_mgr.cleanup()

# ---------------------------------------------------------
# 🤖 4. GENERATE AI README (The Main Engine)
# ---------------------------------------------------------
@app.post("/generate-readme")
async def generate_readme(request: RepoRequest):

    # ✅ CACHE CHECK
    try:
        cached_result = cache_mgr.get_cached_readme(request.url)
        if cached_result:
            print(f"🎯 Cache Hit → {request.url}")
            return cached_result
    except Exception as cache_read_err:
        print(f"⚠️ Cache read failed: {cache_read_err}")

    # ✅ CACHE MISS
    print(f"⚡ Cache Miss → {request.url}")

    git_mgr = GitManager()
    target_path = git_mgr.clone_repo(request.url)

    if not target_path:
        raise HTTPException(
            status_code=400,
            detail="Repository clone failed"
        )

    try:
        # --- CORE ENGINE EXECUTION ---
        print("🚀 Step 1: Scanning...")
        scanner = RepositoryScanner(target_path)
        scanned_data = scanner.scan()

        print("🚀 Step 2: Analyzing...")
        analyzer = ProjectAnalyzer(target_path)
        analysis_report = analyzer.analyze(scanned_data)

        print("🚀 Step 3: Building Report...")
        builder = ReportBuilder(target_path)
        final_report = builder.build(scanned_data, analysis_report)

        # 3. 🤖 CALLING GEMINI (This creates the 'response' variable)
        print("🚀 Step 4: Generating README with Gemini...")
        
        prompt = f"""
You are an Elite Technical Documentation Architect. Your mission is to transform raw JSON metadata into a world-class README.md that screams engineering excellence.

PROJECT DATA:
{final_report}

STRICT ARCHITECTURE & FORMATTING RULES:

1. HEADER & BADGES (Visual Dominance):
   - Start with a clean H1 title.
   - ADD a professional Banner Placeholder: ![Banner](https://socialify.git.ci/{{repo_path}}/network?theme=Dark) (Replace {{repo_path}} with the actual repo path if available, else omit).
   - BADGES: Generate high-quality shields.io badges for every 'key_dependency'.
   - !! CRITICAL !!: All badges MUST be in a single continuous block. Separated ONLY by a space. 
   - DO NOT use newlines, lists, or tables for badges. They must flow as a single horizontal line.

2. EXECUTIVE SUMMARY:
   - Paragraph 1: High-level technical objective.
   - Paragraph 2: Business/Studio impact (use 'extracted_content' for specific achievements like '50+ projects').
   - Use bold text for key metrics.

3. ARCHITECTURE & TECH STACK:
   - Create a clean GitHub Flavored Markdown (GFM) table.
   - Column Headers: | Technology | Version | Key Responsibility |
   - Alignment: | :--- | :--- | :--- |
   - Data Source: 'key_dependencies' and 'primary_stack'. Ensure NO broken pipes or extra dashes.

4. SYSTEM SIGNATURES (The "Deep Scan" Results):
   - Analyze detected 'signatures' (e.g., Magnetic components, handleMouseMove).
   - Explain the technical 'WHY' behind them. (Example: "Framer Motion: Orchestrating complex layout transitions for immersive UX").

5. DIRECTORY BLUEPRINT:
   - Provide an ASCII tree. 
   - Add inline comments (#) explaining the 'Role' of major directories based on common patterns (e.g., src/app -> App Router Logic).

6. DEPLOYMENT & OPERATION:
   - Detect toolchain (npm/yarn/pnpm/mvn) and provide copy-pasteable commands.
   - Sections: Prerequisites, Installation, Local Development, Production Build.

7. ACKNOWLEDGEMENTS & CONTACT:
   - Format contact details with professional icons (📧 Email, 📱 WhatsApp, 📍 Location).
   - Add a 'License' section (default to MIT unless specified).

STRICT FORMATTING RULES:
- VERTICAL SPACING: Use exactly TWO newlines (\\n\\n) between every section, heading, and paragraph.
- HEADINGS: Use proper Markdown headers (##, ###) instead of just bolding text. Never put a heading on the same line as the content.
- LISTS: Every bullet point MUST start on a new line.
- CODE BLOCKS: All terminal commands or file paths MUST be wrapped in triple backticks (```bash ... ```).
- NO CLUTTER: Ensure there is a clear visual break before and after every table or list.

TONE & QUALITY GATE:
- Use active, technical language (e.g., "Leverages", "Orchestrates", "Implements").
- If a section has no data, skip it—DO NOT hallucinate.
- Ensure all Markdown syntax is strictly GFM compliant.
"""

        try:
            # ✅ CORRECT NEW SDK CALL
            gemini_result = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
        except Exception as llm_call_err:
            print("❌ Gemini call crashed:", llm_call_err)
            raise HTTPException(status_code=500, detail="LLM generation crashed")

        # In the new SDK, 'text' is a direct attribute
        markdown = gemini_result.text if gemini_result else None

        if markdown is None:
            raise HTTPException(
                status_code=500,
                detail="Gemini response missing text"
            )

        markdown = markdown.strip()

        if markdown == "":
            raise HTTPException(
                status_code=500,
                detail="Generated README empty"
            )

        # ===== FINAL RESPONSE =====

        final_response = {
            "status": "success",
            "markdown": markdown,
            "metadata": analysis_report
        }

        # ===== CACHE WRITE SAFE =====

        try:
            cache_mgr.set_cached_readme(request.url, final_response)
            print("✅ Cache stored")
        except Exception as cache_write_err:
            print("⚠️ Cache write failed:", cache_write_err)

        return final_response

    except Exception as engine_err:
        print("❌ ENGINE FAILURE:", engine_err)
        raise HTTPException(
            status_code=500,
            detail=str(engine_err)
        )

    finally:
        print("🧹 Cleanup workspace")
        git_mgr.cleanup()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)