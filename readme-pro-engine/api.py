import os
import httpx
import base64
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 🛠️ Core Engine Imports
from core.git_manager import GitManager
from core.scanner import RepositoryScanner
from core.analyzer import ProjectAnalyzer
from core.report_builder import ReportBuilder

# .env file load karo
load_dotenv()

app = FastAPI(title="README_ENGINE_FINAL_V2", version="2.0")

# 🌐 CORS: Iske bina Next.js (Port 3000) API (Port 8000) ko call nahi kar payega
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Gemini & GitHub Config
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-lite') # Recommended for speed/accuracy balance

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

class RepoRequest(BaseModel):
    url: str

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
    
    # URL parsing: https://github.com/owner/repo
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    async with httpx.AsyncClient() as client:
        # Check if README exists to get SHA
        get_res = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents/README.md",
            headers=headers
        )
        sha = get_res.json().get("sha") if get_res.status_code == 200 else None

        # Base64 encoding for GitHub API
        encoded_content = base64.b64encode(content.encode()).decode()

        payload = {
            "message": "🚀 README updated via README ENGINE V2",
            "content": encoded_content,
        }
        if sha: payload["sha"] = sha

        put_res = await client.put(
            f"https://api.github.com/repos/{owner}/{repo}/contents/README.md",
            headers=headers,
            json=payload
        )
        
        if put_res.status_code in [200, 201]:
            return {"status": "success", "url": put_res.json()["content"]["html_url"]}
        
        raise HTTPException(status_code=400, detail=f"GitHub Push Failed: {put_res.text}")

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

        response = model.generate_content(prompt)
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
    git_mgr = GitManager()
    print(f"🔍 Request received for URL: {request.url}") # Log 1
    
    target_path = git_mgr.clone_repo(request.url)
    if not target_path:
        raise HTTPException(status_code=400, detail="Clone Failed")

    try:
        print("🚀 Step 1: Starting Scanner...")
        scanner = RepositoryScanner(target_path)
        scanned_data = scanner.scan()
        print(f"✅ Scanner found {len(scanned_data['code_files'])} files.")

        print("🚀 Step 2: Starting Analyzer...")
        analyzer = ProjectAnalyzer(target_path)
        analysis_report = analyzer.analyze(scanned_data)

        print("🚀 Step 3: Starting Report Builder (Deep Parsing)...")
        builder = ReportBuilder(target_path)
        final_report = builder.build(scanned_data, analysis_report)
        print("✅ Report built successfully.")

        print("🚀 Step 4: Calling Gemini API (This might take a moment)...")
        # AI Prompt
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
- VERTICAL SPACING: Use exactly TWO newlines (\n\n) between every section, heading, and paragraph.
- HEADINGS: Use proper Markdown headers (##, ###) instead of just bolding text. Never put a heading on the same line as the content.
- LISTS: Every bullet point MUST start on a new line.
- CODE BLOCKS: All terminal commands or file paths MUST be wrapped in triple backticks (```bash ... ```).
- NO CLUTTER: Ensure there is a clear visual break before and after every table or list.

TONE & QUALITY GATE:
- Use active, technical language (e.g., "Leverages", "Orchestrates", "Implements").
- If a section has no data, skip it—DO NOT hallucinate.
- Ensure all Markdown syntax is strictly GFM compliant.
"""
        
        # Yahan timeout ka issue ho sakta hai
        response = model.generate_content(prompt)
        print("✅ Gemini responded!")

        return {
            "status": "success",
            "markdown": response.text,
            "metadata": analysis_report
        }

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}") # Har error print hogi
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        print("🧹 Cleaning up...")
        git_mgr.cleanup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)