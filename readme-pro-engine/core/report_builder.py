import os
import json
import sys

# Path handling for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.parser import CodeParser
from config import CONTENT_FILES_KEYWORDS  # Naya import deep extraction ke liye

class ReportBuilder:
    def __init__(self, root_path):
        self.root_path = root_path
        self.parser = CodeParser()

    def build(self, scanned_data, analyzer_report):
        """
        Scanner aur Analyzer ke data ko combine karke final report banata hai.
        Ab ye logic content files (constants/data) ko pehchanta hai.
        """
        final_report = {
            "project_info": analyzer_report,
            "directory_structure": [f["path"] for f in scanned_data["code_files"][:50]], 
            "file_analysis": []
        }

        # Har code file ko process kar rahe hain
        for file_info in scanned_data["code_files"]:
            file_path = os.path.join(self.root_path, file_info["path"])
            file_ext = file_info["extension"]
            
            # 🔍 Logic: Check karo kya ye file 'Deep Content' wali hai?
            # Hum file path me 'constants', 'data', etc. keywords dhoond rahe hain
            is_content_file = any(kw in file_info["path"].lower() for kw in CONTENT_FILES_KEYWORDS)
            
            # Parsing the file with the new flag
            analysis = self.parser.parse(file_path, file_ext, is_content_file=is_content_file)
            
            if "error" not in analysis:
                final_report["file_analysis"].append({
                    "file": file_info["path"],
                    "is_content_data": is_content_file, # AI ko batane ke liye ki ye data file hai
                    "signatures": analysis
                })

        return final_report

    def save_report(self, report, output_path):
        """Report ko JSON file me save karta hai."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False