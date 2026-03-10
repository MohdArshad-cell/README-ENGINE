import os
import httpx # Isse API calls karenge
import base64 # GitHub content encode karne ke liye
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv

# Existing Engine Imports
from core.git_manager import GitManager
from core.scanner import RepositoryScanner
from core.analyzer import ProjectAnalyzer
from core.report_builder import ReportBuilder

load_dotenv()

app = FastAPI()

# 🌐 CORS: Iske bina Next.js API ko call nahi kar payega
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Gemini Setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
class RepoRequest(BaseModel):
    url: str

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

# 2. Direct Push logic
@app.post("/github/push")
async def push_to_github(request: dict):
    token = request.get("token")
    repo_url = request.get("repo_url") 
    content = request.get("content")
    
    # URL se owner aur repo nikalna (Logic: https://github.com/owner/repo)
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    async with httpx.AsyncClient() as client:
        # README dhoondo (SHA nikalne ke liye agar pehle se exist karti hai)
        get_res = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents/README.md",
            headers=headers
        )
        sha = get_res.json().get("sha") if get_res.status_code == 200 else None

        # Update / Create file
        payload = {
            "message": "🚀 README updated via README ENGINE",
            "content": base64.b64encode(content.encode()).decode(),
        }
        if sha: payload["sha"] = sha

        put_res = await client.put(
            f"https://api.github.com/repos/{owner}/{repo}/contents/README.md",
            headers=headers,
            json=payload
        )
        
        if put_res.status_code in [200, 201]:
            return {"status": "success", "url": put_res.json()["content"]["html_url"]}
        raise HTTPException(status_code=400, detail="GitHub Push Failed")

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