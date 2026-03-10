import os

# 1. In folders ko bilkul touch nahi karna (Noise Reduction)
IGNORE_DIRS = {
    '.git', 'node_modules', '__pycache__', 'venv', '.env', 
    'target', 'dist', 'build', '.idea', '.vscode', 'bin', 'obj',
    'coverage', 'logs', 'tmp', 'out'
}

# 2. In file extensions ka code hum analyze karenge (Signature Extraction)
# config.py mein ye line replace kar:
SUPPORTED_EXTENSIONS = {'.java', '.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.cpp'}

# 3. In files ko hum "Identity" aur "Tech Stack" check karne ke liye use karenge
TECH_STACK_FILES = {
    'pom.xml': 'Java/Maven',
    'build.gradle': 'Java/Gradle',
    'package.json': 'Node.js/JS/TS',
    'requirements.txt': 'Python',
    'setup.py': 'Python',
    'go.mod': 'Go',
    'docker-compose.yml': 'Docker/Infrastructure',
    'Dockerfile': 'Docker/Containerization',
    'cargo.toml': 'Rust',
    'composer.json': 'PHP'
}

# 4. Report Limits (To keep AI tokens low)
# Agar file isse badi hai, toh use skip kar denge ya sirf signatures uthayenge
MAX_FILE_SIZE_KB = 100 

# 5. Output Path
REPORT_OUTPUT_FILE = "project_report.json"

# config.py mein ye add kar:
CONTENT_FILES_KEYWORDS = ['constants', 'data', 'content', 'config', 'index']
# In files ka hum poora content ya key-value pairs uthayenge