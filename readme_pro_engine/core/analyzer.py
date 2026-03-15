import os
import sys
import json

# Config import for tech mapping
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import TECH_STACK_FILES

class ProjectAnalyzer:
    def __init__(self, root_path):
        self.root_path = root_path

    def analyze(self, scanned_data):
        """
        Scanned config files ko analyze karke tech stack ki detail nikalta hai.
        """
        report = {
            "primary_stack": "Unknown",
            "detected_frameworks": [],
            "key_dependencies": [],
            "project_type": "Generic"
        }

        config_files = scanned_data.get("config_files", [])
        
        for cfg in config_files:
            file_name = cfg["name"]
            file_path = os.path.join(self.root_path, cfg["path"])

            # 1. Basic Identification from config.py mapping
            if file_name in TECH_STACK_FILES:
                report["primary_stack"] = TECH_STACK_FILES[file_name]

            # 2. Deep Scanning (Content Analysis)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Agar Node.js project hai toh dependencies nikaalo
                    if file_name == 'package.json':
                        data = json.loads(content)
                        deps = data.get('dependencies', {}).keys()
                        dev_deps = data.get('devDependencies', {}).keys()
                        report["key_dependencies"].extend(list(deps) + list(dev_deps))
                        
                        if 'react' in deps: report["detected_frameworks"].append("React")
                        if 'express' in deps: report["detected_frameworks"].append("Express.js")
                        if 'next' in deps: report["detected_frameworks"].append("Next.js")

                    # Agar Java/Maven project hai
                    elif file_name == 'pom.xml':
                        if '<artifactId>spring-boot' in content:
                            report["detected_frameworks"].append("Spring Boot")
                        if '<dependency>' in content:
                            # Basic string search for common Java libs
                            if 'mysql' in content.lower(): report["key_dependencies"].append("MySQL Driver")
                            if 'hibernate' in content.lower(): report["key_dependencies"].append("Hibernate/JPA")

            except Exception as e:
                print(f"Error reading {file_name}: {e}")

        # Final Project Type Deduction
        if any(fw in ["React", "Next.js"] for fw in report["detected_frameworks"]):
            report["project_type"] = "Frontend"
        elif any(fw in ["Spring Boot", "Express.js"] for fw in report["detected_frameworks"]):
            report["project_type"] = "Backend/API"

        return report