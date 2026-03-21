import os
import re
import ast

class CodeParser:
    def __init__(self):
        # 1. Enhanced JS/TS Regex (Handles exports and modern syntax better)
        self.js_func_regex = re.compile(
            r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[\w]+)\s*=>|'  # Arrow functions
            r'(?:export\s+)?function\s+(\w+)\s*\(|'                                    # Standard functions
            r'(?:export\s+)?class\s+(\w+)'                                             # Classes
        )
        
        # 2. Import detection (AI ko batane ke liye ki kaunse external tools use ho rahe hain)
        self.import_regex = re.compile(r'(?:import|from)\s+[\'"](.+?)[\'"]|import\s+(.+?)\s+from')
        
        # 3. Generic logic for Java/C#
        self.generic_class_regex = re.compile(r'class\s+(\w+)')
        self.generic_method_regex = re.compile(r'(public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\)')

    def parse(self, file_path, extension, is_content_file=False):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            res = {"classes": [], "functions": [], "imports": [], "endpoints": []}
            
            # Deep Extraction (Atma Extraction)
            if is_content_file:
                res["extracted_content"] = self._extract_deep_content(content)

            # Language Specific Logic
            if extension == '.py':
                res.update(self._parse_python(content))
            elif extension in ['.js', '.jsx', '.ts', '.tsx']:
                res.update(self._parse_javascript(content))
            else:
                res.update(self._parse_generic(content))
            
            # Common: Extract Imports (Har language ke liye kaam aayega)
            res["imports"] = list(set(re.findall(r'(?:import|from)\s+[\'"](.+?)[\'"]', content)))[:10]
            
            return res
        except Exception as e:
            return {"error": str(e)}

    def _parse_python(self, content):
        """Python AST logic with Scope Awareness (No more double counting)."""
        try:
            tree = ast.parse(content)
            summary = {"classes": [], "functions": []}
            
            for node in tree.body: # Sirf top-level nodes dekho
                if isinstance(node, ast.ClassDef):
                    methods = [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    summary["classes"].append({"name": node.name, "methods": methods})
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    summary["functions"].append(node.name)
            return summary
        except:
            return {"functions": [], "classes": []}

    def _parse_javascript(self, content):
        """React components aur exports ke liye better logic."""
        summary = {"components_or_functions": [], "classes": []}
        
        matches = self.js_func_regex.findall(content)
        for m in matches:
            # Matches tuple: (arrow_func, std_func, class_name)
            name = next((name for name in m if name), None)
            if name:
                if "export class" in content or f"class {name}" in content:
                    summary["classes"].append(name)
                else:
                    summary["components_or_functions"].append(name)
        
        # Clean duplicates
        summary["components_or_functions"] = list(set(summary["components_or_functions"]))
        summary["classes"] = list(set(summary["classes"]))
        return summary

    def _extract_deep_content(self, content):
        """Object/Array extraction logic (Cleansed for AI tokens)."""
        content_map = {}
        # Regex to catch: export const DATA = [...] or export default [...]
        patterns = [
            r'export\s+(?:const|let|var)\s+(\w+)\s*=\s*([\[\{][\s\S]*?[\]\}]);',
            r'export\s+default\s+([\[\{][\s\S]*?[\]\}]);'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                key = match[0] if isinstance(match, tuple) and match[0] else "default_export"
                val = match[1] if isinstance(match, tuple) else match[0]
                # Token reduction: Remove extra spaces and limit size
                clean_val = re.sub(r'\s+', ' ', val).strip()
                content_map[key] = clean_val[:1500] 

        return content_map

    def _parse_generic(self, content):
        return {
            "classes": list(set(self.generic_class_regex.findall(content))),
            "methods": list(set([m[1] for m in self.generic_method_regex.findall(content)]))
        }