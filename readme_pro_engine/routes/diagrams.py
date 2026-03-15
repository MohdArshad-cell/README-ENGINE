from fastapi import APIRouter, HTTPException
import google.generativeai as genai

router = APIRouter()

@app.post("/generate-diagram")
async def generate_diagram(request: dict):
    repo_data = request.get("repo_data") # README scan se jo data mila
    
    prompt = f"""
    Based on this project metadata, generate a Mermaid.js flowchart 
    representing the system architecture. 
    Use 'graph TD' format. Output ONLY the mermaid code.
    Project Data: {repo_data}
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    return {"status": "success", "mermaid_code": response.text}