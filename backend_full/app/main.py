from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.services.github_service import clone_repo, push_new_repo
from app.services.fix_service import fix_repo_code
from app.services.scan_parser import parse_scan_report
from app.database import get_db, CodeReview
from sqlalchemy.orm import Session
import tempfile, shutil, os, json, logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5175", "http://127.0.0.1:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Automated Code Review & Code-Fix Agent",
        "description": "Clone repo, analyze scan report, fix issues, push to new repo",
        "endpoints": {
            "POST /review": "Submit repo_url and scan_report for automated fixing"
        },
        "output_format": {
            "updated_repo_link": "URL of fixed repository",
            "changes_summary": "List of file-wise fixes and optimizations"
        }
    }

@app.post("/review")
async def review(repo_url: str = Form(...), scan_report: UploadFile = File(...), db: Session = Depends(get_db)):
    tmp_dir = None
    try:
        # Read scan report
        report_bytes = await scan_report.read()
        
        # Try to decode as text, if fails keep as bytes for PDF
        try:
            report_text = report_bytes.decode('utf-8')
        except:
            report_text = None
        
        # Create temp directory
        tmp_dir = tempfile.mkdtemp()
        
        # Clone repository
        repo_path = clone_repo(repo_url, tmp_dir)
        
        # Parse scan report (supports PDF and text formats)
        issues = parse_scan_report(report_text, report_bytes)
        
        if not issues:
            return {
                "updated_repo_link": repo_url,
                "change_report": []
            }

        # Fix code based on issues
        changes = fix_repo_code(repo_path, issues)
        
        # Push fixed code to new repo
        new_repo_url = push_new_repo(repo_path, repo_url)

        # Format output according to frontend requirements
        change_report = []
        for change in changes:
            # Create diff string from line changes
            diff_lines = []
            for line_change in change.get('line_changes', []):
                if line_change['change_type'] == 'modified':
                    diff_lines.append(f"- {line_change['original']}")
                    diff_lines.append(f"+ {line_change['fixed']}")
                elif line_change['change_type'] == 'added':
                    diff_lines.append(f"+ {line_change['fixed']}")
                elif line_change['change_type'] == 'removed':
                    diff_lines.append(f"- {line_change['original']}")
            
            change_report.append({
                "file": change['full_path'],
                "issues_fixed": change.get('issues_fixed', []),
                "fix_explanation": change.get('fix_explanation', 'Code fixed'),
                "optimizations": change.get('optimizations', []),
                "total_lines_changed": change.get('total_lines_changed', 0),
                "line_changes": change.get('line_changes', []),
                "diff": "\n".join(diff_lines) if diff_lines else "No changes made"
            })

        # Store in database
        if db:
            try:
                db_review = CodeReview(
                    original_repo_url=repo_url,
                    updated_repo_url=new_repo_url,
                    scan_report=report_text,
                    changes_summary=json.dumps(change_report),
                    diff_content=json.dumps(changes)
                )
                db.add(db_review)
                db.commit()
            except Exception as e:
                logger.error(f"Database error: {e}")
                db.rollback()
        
        return {
            "updated_repo_link": new_repo_url,
            "change_report": change_report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if tmp_dir:
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Cleanup error: {e}")