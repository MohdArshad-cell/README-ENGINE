import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import requests

# Tumhare core modules
from core.scanner import RepositoryScanner
from core.analyzer import ProjectAnalyzer
from core.report_builder import ReportBuilder
from core.git_manager import GitManager
from config import REPORT_OUTPUT_FILE
load_dotenv()
app = FastAPI(title="README_ENGINE_API", version="2.0")

# 🔐 1. CORS Setup (Next.js se baat karne ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class RepoRequest(BaseModel):
    url: str

class PushRequest(BaseModel):
    token: str
    repo_url: str
    content: str

# 🚀 2. ENDPOINT: GENERATE README
@app.post("/generate-readme")
async def generate_readme(request: RepoRequest):
    git_mgr = GitManager()
    url = request.url
    is_remote = url.startswith("http")
    
    target_path = git_mgr.clone_repo(url) if is_remote else url

    if not target_path or not os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="Invalid Target Path")

    try:
        # Step 1: Scanning
        scanner = RepositoryScanner(target_path)
        scanned_data = scanner.scan()

        # Step 2: Analyzing
        analyzer = ProjectAnalyzer(target_path)
        analysis_report = analyzer.analyze(scanned_data)

        # Step 3: Building (Final Markdown)
        builder = ReportBuilder(target_path)
        final_markdown = builder.build(scanned_data, analysis_report)

        # Frontend expects this structure:
        return {
            "markdown": final_markdown,
            "structure": list(scanned_data.get("structure", [])),
            "metadata": {
                "primary_stack": analysis_report.get("primary_stack", "Unknown"),
                "detected_frameworks": analysis_report.get("frameworks", [])
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if is_remote:
            git_mgr.cleanup()

# 🔑 3. ENDPOINT: GITHUB TOKEN EXCHANGE
@app.post("/github/token")
async def get_github_token(request: dict):
    code = request.get("code")
    client_id = os.getenv("NEXT_PUBLIC_GITHUB_CLIENT_ID")
    client_secret = os.getenv("GITHUB_CLIENT_SECRET")

    # Brutal Check: Kya variables mil rahe hain?
    if not client_id or not client_secret:
        print("❌ ERROR: GitHub Credentials Missing in Backend .env")
        return {"error": "Missing credentials in backend"}

    print(f"📡 Exchanging code for token...")
    
    try:
        res = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code
            },
            timeout=10 # Deadline set karo
        )
        data = res.json()
        print(f"✅ GitHub Response: {data}")
        return data
    except Exception as e:
        print(f"🔥 GitHub API Crash: {str(e)}")
        return {"error": str(e)}

# 📤 4. ENDPOINT: DIRECT PUSH TO GITHUB
@app.post("/github/push")
async def push_to_github(request: PushRequest):
    # Logic for GitHub content API (PUT)
    # Isme tum apna purana GitManager logic integrate kar sakte ho
    return {"status": "success", "message": "README pushed to repo"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)