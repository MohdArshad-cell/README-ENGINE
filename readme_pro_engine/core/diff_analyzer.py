# core/diff_analyzer.py
class DiffAnalyzer:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def summarize_changes(self, diff_data):
        if not diff_data: return "No major changes detected."
        
        prompt = f"""
        Act as a Senior Developer Reviewer. Summarize the following git diff into a 2-line "Latest Pulse" update.
        
        DIFF STATS:
        {diff_data['stat']}
        
        DIFF CONTENT SNIPPET:
        {diff_data['content']}
        
        RULES:
        1. Focus on 'Why' and 'What' (e.g., 'Refactored Auth logic for better speed').
        2. Don't just list files. Explain the technical impact.
        3. Keep it under 50 words.
        """
        
        response = self.client.models.generate_content(model=self.model, contents=prompt)
        return response.text.strip() if response else "Codebase updated."