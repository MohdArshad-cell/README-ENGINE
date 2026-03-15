import os
import re
import ast

class CodeParser:
    def __init__(self):
        # 1. Java/C++/C# style methods regex
        self.generic_method_regex = re.compile(r'(public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *\{?')
        
        # 2. Modern JS/TS/React Functional Components & Arrow Functions
        # Pakadta hai: const MyComponent = () => ..., function MyFunc() ...
        self.js_func_regex = re.compile(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[\w]+)\s*=>|function\s+(\w+)\s*\(')
        
        # 3. Class detection for most languages
        self.generic_class_regex = re.compile(r'class\s+(\w+)')
        
        # 4. API Endpoints detection (Spring Boot, Express, etc.)
        self.endpoint_regex = re.compile(r'@(Get|Post|Put|Delete|Patch)Mapping\(.*?"(.*?)"|app\.(get|post|put|delete)\(.*?"(.*?)"')

    def parse(self, file_path, extension, is_content_file=False):
        """
        Main entry point for parsing. 
        is_content_file=True hone par ye file ke andar ka asali data (projects, lists) bhi nikalega.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Deep Extraction: Agar file 'constants' ya 'data' wali hai toh content scan karo
            deep_data = {}
            if is_content_file:
                deep_data = self._extract_deep_content(content)

            # Language specific parsing
            if extension == '.py':
                res = self._parse_python(content)
            elif extension in ['.js', '.jsx', '.ts', '.tsx']:
                res = self._parse_javascript(content)
            else:
                res = self._parse_generic(content)
            
            # Agar deep data mila hai toh use result me merge karo
            if deep_data:
                res["extracted_content"] = deep_data
            
            return res
        except Exception as e:
            return {"error": str(e)}

    def _extract_deep_content(self, content):
        """
        Exported objects, arrays aur constants se actual text (Atma) nikalta hai.
        """
        content_map = {}
        # Regex to find exported constants/objects like: export const projects = [...]
        patterns = [
            r'export\s+const\s+(\w+)\s*=\s*(\[[\s\S]*?\]|\{[\s\S]*?\});',
            r'export\s+default\s+(\[[\s\S]*?\]|\{[\s\S]*?\});'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Key-Value pair set karna (Project list ya Config object)
                key = match[0] if isinstance(match, tuple) and match[0] else "default_export"
                value = match[1] if isinstance(match, tuple) else match[0]
                
                # Cleaning: Faltu spaces nikaalna taaki AI ko kam tokens bhejne padein
                clean_value = re.sub(r'\s+', ' ', value).strip()
                content_map[key] = clean_value[:2000] # 2000 chars limit per object

        return content_map

    def _parse_javascript(self, content):
        """React aur Modern JS ke liye logic."""
        summary = {"components_or_functions": [], "classes": [], "endpoints": []}
        
        # Functions/Components extraction
        matches = self.js_func_regex.findall(content)
        for m in matches:
            func_name = m[0] if m[0] else m[1]
            if func_name and func_name not in summary["components_or_functions"]:
                summary["components_or_functions"].append(func_name)
        
        # Classes extraction
        summary["classes"] = list(set(self.generic_class_regex.findall(content)))
        
        # Endpoint extraction
        endpoints = self.endpoint_regex.findall(content)
        for ep in endpoints:
            clean_ep = next((item for item in ep if item.startswith('/')), None)
            if clean_ep: summary["endpoints"].append(clean_ep)
            
        return summary

    def _parse_python(self, content):
        """Python files ke liye AST (Abstract Syntax Tree) logic."""
        try:
            tree = ast.parse(content)
            summary = {"classes": [], "functions": []}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    summary["classes"].append({"name": node.name, "methods": methods})
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Check if it's a top-level function
                    summary["functions"].append(node.name)
            return summary
        except:
            return {"error": "Failed to parse Python AST"}

    def _parse_generic(self, content):
        """Java, C++, etc. ke liye default Regex logic."""
        return {
            "classes": list(set(self.generic_class_regex.findall(content))),
            "methods": list(set([m[1] for m in self.generic_method_regex.findall(content)])),
            "endpoints": []
        }