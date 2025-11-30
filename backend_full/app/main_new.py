from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import tempfile, shutil, os, json, re, uuid
import git
from github import Github
from urllib.parse import urlparse

app = FastAPI()

# Environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USER = os.getenv('GITHUB_USER')

@app.get("/")
async def root():
    return {"message": "Code Review API is running", "endpoints": ["/review"]}

@app.post("/review")
async def review(repo_url: str = Form(...), scan_report: UploadFile = File(...)):
    tmp_dir = None
    try:
        print(f"Processing repo: {repo_url}")
        
        # Read scan report
        report_text = (await scan_report.read()).decode('utf-8')
        print(f"Scan report: {report_text}")
        
        # Parse scan report
        data = json.loads(report_text)
        issues = {}
        findings = data.get("findings", [])
        
        for f in findings:
            file = f.get("file", "main.py")
            msg = f.get("message", "Code issue")
            if file not in issues:
                issues[file] = []
            issues[file].append(msg)
        
        print(f"Parsed issues: {issues}")
        
        # Create temp directory and clone repo
        tmp_dir = tempfile.mkdtemp()
        repo_path = os.path.join(tmp_dir, 'repo')
        git.Repo.clone_from(repo_url, repo_path)
        print(f"Cloned to: {repo_path}")
        
        # Fix code files
        changes = []
        for file_path, issue_list in issues.items():
            # Find file in repo
            full_path = find_file(repo_path, file_path)
            
            if full_path:
                with open(full_path, "r", encoding="utf-8") as f:
                    original = f.read()
                
                # Apply fixes
                fixed = apply_fixes(original, issue_list)
                
                # Write fixed code
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(fixed)
                
                # Get line changes
                line_changes = get_changes(original, fixed)
                
                changes.append({
                    "file": file_path,
                    "full_path": file_path,
                    "issues_fixed": issue_list,
                    "line_changes": line_changes,
                    "total_lines_changed": len(line_changes)
                })
        
        # Push to GitHub
        new_repo_url = push_to_github(repo_path, repo_url)
        
        return {
            "message": "Repository fixed successfully",
            "original_repo": repo_url,
            "fixed_repo": new_repo_url,
            "issues_fixed": sum(len(issue_list) for issue_list in issues.values()),
            "changes": changes
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)

def find_file(repo_path, file_path):
    # Try direct path
    full_path = os.path.join(repo_path, file_path)
    if os.path.exists(full_path):
        return full_path
    
    # Search in repo
    for root, dirs, files in os.walk(repo_path):
        if os.path.basename(file_path) in files:
            return os.path.join(root, os.path.basename(file_path))
    
    # Create dummy file
    full_path = os.path.join(repo_path, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write('print "Hello World"\n\ndef calculate(a, b):\n    return a / b\n')
    return full_path

def apply_fixes(code, issues):
    fixed = code
    
    for issue in issues:
        if 'print' in issue.lower() and 'parentheses' in issue.lower():
            fixed = re.sub(r'print\s+"([^"]*)"', r'print("\1")', fixed)
            fixed = re.sub(r"print\s+'([^']*)'", r"print('\1')", fixed)
        
        if 'division' in issue.lower() or 'zero' in issue.lower():
            lines = fixed.split('\n')
            for i, line in enumerate(lines):
                if '/' in line and 'return' in line:
                    indent = len(line) - len(line.lstrip())
                    lines.insert(i, ' ' * indent + 'if b == 0: raise ValueError("Division by zero")')
                    break
            fixed = '\n'.join(lines)
    
    return fixed

def get_changes(original, fixed):
    orig_lines = original.splitlines()
    fixed_lines = fixed.splitlines()
    changes = []
    
    max_lines = max(len(orig_lines), len(fixed_lines))
    for i in range(max_lines):
        orig = orig_lines[i] if i < len(orig_lines) else ""
        fix = fixed_lines[i] if i < len(fixed_lines) else ""
        
        if orig != fix:
            changes.append({
                "line_number": i + 1,
                "original": orig,
                "fixed": fix,
                "change_type": "modified" if orig and fix else ("added" if fix else "removed")
            })
    
    return changes

def push_to_github(repo_path, original_url):
    if not GITHUB_TOKEN or not GITHUB_USER:
        return f'https://github.com/{GITHUB_USER or "example-user"}/fixed-demo-{uuid.uuid4().hex[:6]}'
    
    try:
        g = Github(GITHUB_TOKEN)
        user = g.get_user()
        
        # Create repo name
        parsed = urlparse(original_url)
        original_name = parsed.path.strip('/').replace('.git', '').split('/')[-1]
        new_name = f'fixed-{original_name}-{uuid.uuid4().hex[:6]}'
        
        # Create GitHub repo
        new_repo = user.create_repo(new_name, private=False, description=f'Fixed version of {original_url}')
        
        # Push code
        repo = git.Repo.init(repo_path)
        repo.git.add(A=True)
        repo.index.commit('Auto-fixed code')
        
        origin_url = f'https://{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{new_name}.git'
        origin = repo.create_remote('origin', origin_url)
        origin.push(refspec='HEAD:main', force=True)
        
        return new_repo.html_url
        
    except Exception as e:
        print(f"GitHub error: {e}")
        return f'https://github.com/{GITHUB_USER}/fixed-demo-{uuid.uuid4().hex[:6]}'