import os
import sys
import json

# Config import for tech mapping
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import TECH_STACK_FILES

class ProjectAnalyzer:
    def __init__(self, root_path):
        self.root_path = root_path #

    def categorize_modules(self, code_modules):
        """
        Code modules ko unke path aur signatures ke basis par categorize karta hai.
        Taki AI ko pata chale ki Controller kahan hai aur Database logic kahan.
        """
        categories = {
            "api_gateway": [],    # Routes, Controllers, Endpoints
            "business_logic": [], # Services, Managers, Core Logic
            "data_layer": [],     # Models, Schemas, Repositories
            "utility": []         # Helpers, Utils, Configs
        }

        for module in code_modules:
            path_lower = module["path"].lower()
            signatures = module.get("signatures", [])
            
            # Logic: Path keywords aur function names se role pehchanno
            if any(x in path_lower for x in ['api', 'route', 'controller', 'endpoint']):
                categories["api_gateway"].append(module)
            elif any(x in path_lower for x in ['model', 'schema', 'db', 'entity', 'repository']):
                categories["data_layer"].append(module)
            elif any(x in path_lower for x in ['service', 'logic', 'manager', 'core']):
                categories["business_logic"].append(module)
            else:
                categories["utility"].append(module)
        
        return categories

    def analyze(self, scanned_data):
        """
        Updated Analysis:
        1. Config analysis (Tech Stack)
        2. Module Categorization (Architecture)
        3. Project Type Deduction
        """
        report = {
            "primary_stack": "Unknown", #
            "detected_frameworks": [], #
            "key_dependencies": [], #
            "module_map": {},
            "directory_tree": scanned_data.get("directory_tree", ""),
            "project_complexity": "Low"
        }

        # 1. ANALYZE CONFIG FILES (Tech Stack Discovery)
        config_files = scanned_data.get("config_files", []) #
        for cfg in config_files:
            file_name = cfg["name"]
            file_path = os.path.join(self.root_path, cfg["path"]) #

            if file_name in TECH_STACK_FILES: #
                report["primary_stack"] = TECH_STACK_FILES[file_name] #

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if file_name == 'package.json': #
                        data = json.loads(content) #
                        deps = list(data.get('dependencies', {}).keys()) #
                        report["key_dependencies"].extend(deps) #
                        
                        if 'react' in deps: report["detected_frameworks"].append("React") #
                        if 'next' in deps: report["detected_frameworks"].append("Next.js") #
                        if 'fastapi' in content.lower(): report["detected_frameworks"].append("FastAPI")
            except:
                continue

        # 2. ANALYZE CODE MODULES (Architecture Discovery)
        code_modules = scanned_data.get("code_modules", [])
        report["module_map"] = self.categorize_modules(code_modules)
        
        # 3. COMPLEXITY DEDUCTION
        total_modules = len(code_modules)
        if total_modules > 20: report["project_complexity"] = "High"
        elif total_modules > 10: report["project_complexity"] = "Medium"

        return report