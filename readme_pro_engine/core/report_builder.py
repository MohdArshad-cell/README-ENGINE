import os
import json
import sys

# Path handling for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ReportBuilder:
    def __init__(self, root_path):
        self.root_path = root_path

    def build(self, scanned_data, analyzer_report):
        """
        Synthesizes Scanner and Analyzer data into a high-density architectural report.
        AI ko ab poora 'System Map' milega, sirf file list nahi.
        """
        # 1. Basic Metadata
        final_report = {
            "tech_stack": {
                "primary": analyzer_report.get("primary_stack"),
                "frameworks": analyzer_report.get("detected_frameworks"),
                "dependencies": analyzer_report.get("key_dependencies")[:20] # Filtered for noise
            },
            "architecture_map": analyzer_report.get("module_map", {}),
            "directory_insight": scanned_data.get("directory_tree", ""),
            "deep_analysis": []
        }

        # 2. High-Value File Analysis
        # Hum sirf un files ka deep signatures bhejenge jo key layers mein hain
        module_map = analyzer_report.get("module_map", {})
        
        # Priority check: API Gateway aur Business Logic ko pehle lo
        priority_layers = ['api_gateway', 'business_logic', 'data_layer']
        
        for layer in priority_layers:
            for module in module_map.get(layer, []):
                final_report["deep_analysis"].append({
                    "role": layer.upper(),
                    "file": module["path"],
                    "signatures": module.get("signatures", []),
                    "impact": f"Handles {layer.replace('_', ' ')} logic"
                })

        # 3. Project Health/Complexity Summary
        final_report["summary"] = {
            "complexity": analyzer_report.get("project_complexity"),
            "total_modules": len(scanned_data.get("code_modules", [])),
            "config_files_found": [cfg["name"] for cfg in scanned_data.get("config_files", [])]
        }

        return final_report

    def get_raw_text(self, report):
        """Report ko ek readable string me convert karta hai Gemini prompt ke liye."""
        return json.dumps(report, indent=2)

    def save_report(self, report, output_path):
        """Debugging ke liye JSON save karo."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4)
            return True
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False