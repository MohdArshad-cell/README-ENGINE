import os, time, httpx, base64, hmac, hashlib, jwt, uuid, json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

# 🛠️ Core Engine Imports (Classes core folder se hi aayengi)
from core.git_manager import GitManager
from core.scanner import RepositoryScanner
from core.analyzer import ProjectAnalyzer
from core.report_builder import ReportBuilder
from core.cache_manager import cache_mgr
from core.security_scanner import SecretScanner


load_dotenv()

app = FastAPI(title="README_ENGINE_PRO", version="2.0")

# 🌐 CORS Configuration
origins = ["https://readme-engine.vercel.app", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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



WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")





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
    # 1. Setup & Logging
    task_id = f"{installation_id}_{int(time.time())}"
    print(f"🤖 Universal Bot started | Task: {task_id} | Repo: {repo_url}")
    
    # 2. Get Installation Token
    token = get_installation_token(installation_id)
    if not token:
        print(f"❌ [{task_id}] Could not generate installation token. Aborting.")
        return

    # 3. Authenticated Cloning
    auth_repo_url = repo_url.replace("https://", f"https://x-access-token:{token}@")
    unique_folder = f"temp_repo_{task_id}"
    git_mgr = GitManager(temp_dir=unique_folder)
    
    target_path = git_mgr.clone_repo(auth_repo_url)
    if not target_path:
        print(f"❌ [{task_id}] Failed to clone repo.")
        return

    try:
        # 🛡️ STEP 1: Security Scan
        from core.security_scanner import SecretScanner
        security_findings = SecretScanner().scan(target_path)
        security_alert_text = "\n".join(security_findings) if security_findings else "Safe."

        # 📊 STEP 2: Project Analysis
        scanner = RepositoryScanner(target_path)
        data = scanner.scan()
        analyzer = ProjectAnalyzer(target_path)
        report = analyzer.analyze(data)
        builder = ReportBuilder(target_path)
        final_report = builder.build(data, report)
        #

        # 🎨 STEP 3: Themed Mermaid Generation
        print(f"🎨 [{task_id}] Generating THEMED Architecture Diagram...")
        
        # 💡 PRO TIP: Hum Mermaid ko 'dark' theme aur 'blue' accent colors ke liye force kar rahe hain
        diagram_prompt = f"""
        Generate a professional Mermaid.js 'graph TD' flowchart.
        
        CONTEXT: {report.get('primary_stack')} | {report.get('key_dependencies')[:10]}
        
        STYLE RULES:
        1. Start with this exact directive for a Dark/Blue theme:
           %%{{init: {{'theme': 'base', 'themeVariables': {{ 'primaryColor': '#1e40af', 'primaryTextColor': '#fff', 'primaryBorderColor': '#3b82f6', 'lineColor': '#60a5fa', 'secondaryColor': '#111827', 'tertiaryColor': '#1f2937'}}}}}}%%
        2. Format: A["Label"] --> B["Label"]
        3. Output ONLY the raw Mermaid code.
        """
        
        # ⚠️ NOTE: Model version ko 'gemini-2.0-flash-lite' rakho, 2.5 abhi exist nahi karta.
        #
        diagram_res = client.models.generate_content(model="gemini-2.5-flash-lite", contents=diagram_prompt)
        mermaid_code = diagram_res.text.strip() if diagram_res else ""

        # 📝 STEP 4: Master README Synthesis
        final_prompt = f"""
        Act as a Senior Architect. Synthesize a README.md.
        SECURITY FINDINGS: {security_alert_text}
        MERMAID DIAGRAM: {mermaid_code}
        PROJECT DATA: {final_report}
        
        LAYOUT:
        - Header with Badges
        - ⚠️ SECURITY ALERT (If applicable)
        - ## 📊 System Architecture
          Insert Mermaid code block here.
        - ## 🚀 Quick Start & Features
        """
        
        gemini_result = client.models.generate_content(model=GEMINI_MODEL, contents=final_prompt)
        markdown = gemini_result.text if gemini_result else ""

        if not markdown: 
            print(f"⚠️ [{task_id}] Gemini returned empty text.")
            return

        # 🚀 STEP 5: GITHUB ACTION - CREATE PR
        parts = repo_url.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
        
        async with httpx.AsyncClient() as http_client:
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            base_url = f"[https://api.github.com/repos/](https://api.github.com/repos/){owner}/{repo}"

            # Step A: Get README SHA
            content_res = await http_client.get(f"{base_url}/contents/README.md", headers=headers)
            current_sha = content_res.json().get("sha") if content_res.status_code == 200 else None

            # Step B: Create Branch
            new_branch = f"readme-ai-{task_id}"
            main_ref = await http_client.get(f"{base_url}/git/ref/heads/{branch}", headers=headers)
            main_sha = main_ref.json()["object"]["sha"]

            await http_client.post(f"{base_url}/git/refs", headers=headers, json={
                "ref": f"refs/heads/{new_branch}",
                "sha": main_sha
            })

            # Step C: Commit File
            encoded_content = base64.b64encode(markdown.encode()).decode()
            await http_client.put(f"{base_url}/contents/README.md", headers=headers, json={
                "message": "docs: AI Documentation & Security Update 🤖",
                "content": encoded_content,
                "branch": new_branch,
                "sha": current_sha
            })

            # Step D: Open PR
            pr_body = f"## AI Analysis Complete 🤖\nDetected a code push on `{branch}`."
            if security_findings:
                pr_body += "\n\n### 🚨 SECURITY WARNING\nPotential secrets were found. Check the README and revoke them ASAP!"
            
            pr_body += f"\n\n### 📊 Visuals Included\nGenerated a new Architecture Diagram based on the latest push."
            pr_body += "\n\n_Generated by **README-ENGINE-PRO**_"

            pr_res = await http_client.post(f"{base_url}/pulls", headers=headers, json={
                "title": "📝 AI Documentation & Security Update",
                "body": pr_body,
                "head": new_branch,
                "base": branch
            })

            if pr_res.status_code == 201:
                print(f"🎉 SUCCESS! PR opened: {pr_res.json().get('html_url')}")
            else:
                print(f"⚠️ PR Failed: {pr_res.text}")

    except Exception as e:
        print(f"❌ [{task_id}] Critical Error: {e}")
    finally:
        # 6. Cleanup (Always cleanup unique folders)
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

    # 1. Concurrency Fix: Har request ke liye unique folder
    task_id = f"diag_{uuid.uuid4().hex[:8]}"
    unique_folder = f"temp_{task_id}"
    git_mgr = GitManager(temp_dir=unique_folder)
    
    target_path = git_mgr.clone_repo(repo_url)
    if not target_path:
        raise HTTPException(status_code=400, detail="Repository clone failed")
    
    try:
        # 📊 Deep Analysis for Context
        scanner = RepositoryScanner(target_path)
        data = scanner.scan()
        analyzer = ProjectAnalyzer(target_path)
        report = analyzer.analyze(data)

        # 🚀 Enhanced Context for Gemini
        # Sirf structure nahi, hum important patterns dhoond rahe hain
        full_context = {
            "stack": report.get("primary_stack"),
            "structure": list(data.get("structure", []))[:50],
            "frameworks": report.get("detected_frameworks"),
            "entry_points": [f for f in data.get("structure", []) if any(x in f.lower() for x in ['main.py', 'api.py', 'app.tsx', 'index.ts'])]
        }

        # 🎯 THE MASTER PROMPT: Logical Layering Force karo
# 🎯 THE ELITE ARCHITECT PROMPT
        prompt = f"""
Act as a Staff Software Engineer & System Architect. Your goal is to generate a professional, high-level Architecture Diagram using Mermaid.js (graph TD).

--- PROJECT CONTEXT ---
Stack: {full_context['stack']}
Frameworks: {full_context['frameworks']}
Key Entry Points: {full_context['entry_points']}
File Structure Snippet: {full_context['structure']}

--- DESIGN PHILOSOPHY ---
1. LAYERING: Organize the diagram into clear logical subgraphs:
   - 'User_Interface' (Frontend components/pages)
   - 'API_Gateway_Routes' (Controllers, Endpoints, Request Handling)
   - 'Business_Logic_Services' (Core functions, Analyzers, Managers)
   - 'Data_Infrastructure' (Databases, Cache, External APIs, File Systems)

2. FLOW LOGIC: Use directional arrows (-->) to show how a user request flows from the UI through the API to the Logic layer and finally to Data/Cache.

3. VISUAL STYLE: Use the following branding directive at the very top:
   %%{{init: {{'theme': 'base', 'themeVariables': {{ 
     'primaryColor': '#1e40af', 
     'primaryTextColor': '#fff', 
     'primaryBorderColor': '#3b82f6', 
     'lineColor': '#60a5fa', 
     'secondaryColor': '#111827',
     'tertiaryColor': '#020203'
   }}}}}}%%

--- CONSTRAINTS ---
- Use ONLY Alphanumeric characters and spaces inside quotes for labels, e.g., ID["Display Name"].
- DO NOT use special characters like '(', ')', '/', or '\\' inside labels as they crash Mermaid.
- Output ONLY the raw Mermaid code. No markdown formatting.
- If a layer is missing in the context, do not hallucinate; only map what is visible.
"""

        # ⚠️ Model version 2.0-flash-lite hi use karna
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        
        raw_code = response.text.replace("```mermaid", "").replace("```", "").strip()

        # 🧹 Robust Cleaning Logic
        import re
        if not raw_code.startswith("graph TD"):
            raw_code = "graph TD\n" + raw_code
        
        # Remove characters that break Mermaid rendering
        raw_code = raw_code.replace("(", " ").replace(")", " ").replace("\\", "/")

        return {
            "status": "success",
            "mermaid_code": raw_code,
            "metadata": {"stack": report.get("primary_stack")}
        }
    finally:
        git_mgr.cleanup()
# ---------------------------------------------------------
# 🤖 4. GENERATE AI README (The Main Engine)
# ---------------------------------------------------------
@app.post("/generate-readme")
async def generate_readme(request: RepoRequest):
    # 1. CACHE CHECK
    try:
        cached_result = cache_mgr.get_cached_readme(request.url)
        if cached_result:
            print(f"🎯 Cache Hit → {request.url}")
            return cached_result
    except Exception as e:
        print(f"⚠️ Cache read failed: {e}")

    # 2. CLONE & SETUP
    # Unique folder logic for concurrency safety
    task_id = f"manual_{uuid.uuid4().hex[:8]}"
    git_mgr = GitManager(temp_dir=f"temp_{task_id}")
    target_path = git_mgr.clone_repo(request.url)

    if not target_path:
        raise HTTPException(status_code=400, detail="Repository clone failed")

    try:
        # 🛡️ STEP 1: Deep Scanning & Security
        scanner = RepositoryScanner(target_path)
        scanned_data = scanner.scan() # Ab isme Tree aur Signatures hain
        
        from core.security_scanner import SecretScanner
        security_findings = SecretScanner().scan(target_path)
        security_alert = "\n".join(security_findings) if security_findings else "No leaks found."

        # 📊 STEP 2: Architecture Analysis
        analyzer = ProjectAnalyzer(target_path)
        analysis_report = analyzer.analyze(scanned_data) # Ab isme Module Map hai

        # 🏗️ STEP 3: Master Report Building
        builder = ReportBuilder(target_path)
        final_report = builder.build(scanned_data, analysis_report)

        # 🤖 STEP 4: GENERATE WITH "GOD-TIER" PROMPT
        print("🚀 Calling Gemini for Deep Documentation...")
        
        # Mermaid code generator logic (internal call for better structure)
        mermaid_prompt = f"Generate only a Mermaid.js 'graph TD' code for this architecture: {analysis_report.get('module_map')}"
        mermaid_res = client.models.generate_content(model=GEMINI_MODEL, contents=mermaid_prompt)
        mermaid_code = mermaid_res.text.strip() if mermaid_res else ""

        master_prompt = f"""
You are a Principal Software Architect at a FAANG company. Your task is to document this repository with extreme precision and engineering depth. 

--- SYSTEM METADATA ---
Report: {final_report}
Security Status: {security_alert}
Mermaid Architecture: {mermaid_code}

--- MANDATORY README STRUCTURE ---

1. PROJECT TITAN (H1): 
   - A bold title followed by professional badges for the tech stack.
   - Banner: ![Banner](https://socialify.git.ci/{request.url.split('/')[-2]}/{request.url.split('/')[-1]}/network?theme=Dark)

2. ⚠️ SECURITY DISCLOSURE:
   - IF Security Status is not 'Safe', create a HIGH-PRIORITY alert box listing leaked files and mandatory rotation steps.

3. 🏛️ ARCHITECTURAL BLUEPRINT:
   - Provide a high-level summary of the system design (e.g., Microservices, Monolith, MVC).
   - INSERT the provided Mermaid diagram in a code block: ```mermaid\\n{mermaid_code}\\n```.
   - Explain the "Data Journey": How a request flows from the API Gateway to the Business Logic and finally to the Data Layer.

4. 🧬 DEEP MODULE INTELLIGENCE:
   - Use the 'Deep Analysis' data to explain the core modules.
   - DO NOT just list files. Explain the "Signatures" (Functions/Classes) found. 
   - Example: "`auth_manager.py` orchestrates JWT validation and session persistence using the `validate_token` signature."

5. 🌳 DIRECTORY HIERARCHY:
   - Provide the ASCII tree from the metadata. 
   - Add concise inline comments for the role of each primary directory.

6. ⚙️ INFRASTRUCTURE & OPS:
   - Detect and list setup commands (npm, pip, mvn, etc.)
   - Include sections for: Environment Variables (.env), Local Development, and Production Build.

7. 🛠️ TECH STACK TABLE:
   - A clean GFM table: | Component | Technology | Role |

--- FORMATTING & TONE RULES ---
- Use "Engineer-to-Engineer" tone: Technical, precise, and devoid of fluff.
- Use exactly TWO newlines between sections for maximum scannability.
- All code, file paths, and signatures MUST be in backticks.
- NEVER hallucinate a feature. If the data isn't there, omit the section.
"""

        gemini_result = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=master_prompt
        )
        
        markdown = gemini_result.text.strip() if gemini_result else ""

        if not markdown:
            raise HTTPException(status_code=500, detail="Gemini failed to generate content")

        # 5. RESPONSE & CACHE
        response_data = {
            "status": "success",
            "markdown": markdown,
            "metadata": analysis_report
        }
        
        try:
            cache_mgr.set_cached_readme(request.url, response_data)
        except:
            pass

        return response_data

    except Exception as e:
        print(f"❌ ENGINE CRASH: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        git_mgr.cleanup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)