import os
import argparse
from core.scanner import RepositoryScanner
from core.analyzer import ProjectAnalyzer
from core.report_builder import ReportBuilder
from core.git_manager import GitManager  # Naya Manager
from config import REPORT_OUTPUT_FILE

def run_engine(path_or_url):
    git_mgr = GitManager()
    is_remote = path_or_url.startswith("http")
    
    # Agar URL hai toh clone karo, varna local path use karo
    target_path = git_mgr.clone_repo(path_or_url) if is_remote else path_or_url

    if not target_path or not os.path.exists(target_path):
        print("❌ Error: Target path invalid.")
        return

    try:
        print(f"🚀 Starting Extraction Engine...")

        # Step 1: Scanning
        scanner = RepositoryScanner(target_path)
        scanned_data = scanner.scan()

        # Step 2: Analyzing
        analyzer = ProjectAnalyzer(target_path)
        analysis_report = analyzer.analyze(scanned_data)

        # Step 3 & 4: Parsing & Building
        builder = ReportBuilder(target_path)
        final_report = builder.build(scanned_data, analysis_report)

        # Step 5: Saving
        builder.save_report(final_report, REPORT_OUTPUT_FILE)
        
        print("-" * 30)
        print(f"🔥 SUCCESS! Report generated at: {REPORT_OUTPUT_FILE}")
        print("-" * 30)

    finally:
        # Step 6: Cleanup (Sirf agar remote clone kiya tha)
        if is_remote:
            git_mgr.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Project Metadata")
    parser.add_argument("--input", type=str, help="GitHub URL or Local Path", required=True)
    
    args = parser.parse_args()
    run_engine(args.input)