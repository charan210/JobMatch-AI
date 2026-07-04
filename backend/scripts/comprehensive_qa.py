import asyncio
import httpx
import os
import json
import time
from sqlalchemy.ext.asyncio import create_async_engine

BASE_URL = "http://127.0.0.1:8000"
DB_URL = "postgresql+asyncpg://postgres:12345678@localhost:5433/aras_db"
REDIS_URL = "redis://localhost:6379/0"

REPORT = {
    "environment": {},
    "authentication": {},
    "coverage": [],
    "performance": {},
    "database": {},
    "async_pipeline": {},
    "security": [],
    "bugs": [],
    "warnings": [],
    "passed": 0,
    "failed": 0
}

async def verify_environment():
    try:
        engine = create_async_engine(DB_URL)
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        REPORT["environment"]["postgres"] = "UP"
    except Exception as e:
        REPORT["environment"]["postgres"] = f"DOWN: {e}"
        return False

    import redis.asyncio as redis
    try:
        r = redis.from_url(REDIS_URL)
        await r.ping()
        REPORT["environment"]["redis"] = "UP"
    except Exception as e:
        REPORT["environment"]["redis"] = f"DOWN: {e}"
        return False

    if not os.environ.get("GEMINI_API_KEY") and not os.path.exists(".env"):
        REPORT["environment"]["gemini"] = "MISSING"
    else:
        REPORT["environment"]["gemini"] = "CONFIGURED"

    return True

async def test_endpoint(client, name, method, url, **kwargs):
    start = time.time()
    try:
        res = await client.request(method, f"{BASE_URL}{url}", **kwargs)
        duration = time.time() - start
        REPORT["coverage"].append({
            "name": name,
            "endpoint": url,
            "method": method,
            "status_code": res.status_code,
            "duration": duration,
            "result": "PASS" if res.status_code < 400 else "FAIL",
            "response": res.text[:200]
        })
        return res, duration
    except Exception as e:
        duration = time.time() - start
        REPORT["coverage"].append({
            "name": name,
            "endpoint": url,
            "method": method,
            "status_code": None,
            "duration": duration,
            "result": "FAIL",
            "response": str(e)
        })
        return None, duration

async def main():
    if not await verify_environment():
        print("Environment failed.")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Auth
        user_email = "mayur@gmail.com"
        password = "mayur@123"
        
        # Register
        res, _ = await test_endpoint(client, "Register", "POST", "/api/v1/auth/register", json={
            "email": user_email, "password": password, "first_name": "Mayur", "last_name": "QA"
        })
        
        # Login
        res, _ = await test_endpoint(client, "Login", "POST", "/api/v1/auth/login", json={
            "username": user_email, "password": password
        })
        
        token = res.json().get("access_token") if res and res.status_code == 200 else None
        refresh = res.json().get("refresh_token") if res and res.status_code == 200 else None
        
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        # Health
        await test_endpoint(client, "Health Base", "GET", "/health")
        await test_endpoint(client, "Health Detailed", "GET", "/api/v1/health/detailed")
        
        # Users
        await test_endpoint(client, "Get Me", "GET", "/api/v1/users/me", headers=headers)
        
        # Jobs
        job_payload = {
            "title": "QA Engineer",
            "department": "Engineering",
            "location": "Remote",
            "description": "QA tester job."
        }
        res, _ = await test_endpoint(client, "Create Job", "POST", "/jobs", json=job_payload, headers=headers)
        job_id = res.json().get("id") if res and res.status_code == 201 else None
        
        await test_endpoint(client, "List Jobs", "GET", "/jobs", headers=headers)
        if job_id:
            await test_endpoint(client, "Get Job", "GET", f"/jobs/{job_id}", headers=headers)
        
        # Candidates
        c_payload = {
            "first_name": "Candidate",
            "last_name": "One",
            "email": "cand1@example.com"
        }
        res, _ = await test_endpoint(client, "Create Candidate", "POST", "/candidates", json=c_payload, headers=headers)
        candidate_id = res.json().get("id") if res and res.status_code == 201 else None
        
        await test_endpoint(client, "List Candidates", "GET", "/candidates", headers=headers)
        if candidate_id:
            await test_endpoint(client, "Get Candidate", "GET", f"/candidates/{candidate_id}", headers=headers)
        
        # Upload resume
        resume_path = r"D:\Projects\AI-Recruitment-System\tests\fixtures\resumes\sample_resume.pdf"
        resume_id = None
        if os.path.exists(resume_path) and candidate_id:
            with open(resume_path, "rb") as f:
                res, _ = await test_endpoint(client, "Upload Resume", "POST", "/resumes/upload", data={"candidate_id": candidate_id}, files={"file": ("sample_resume.pdf", f, "application/pdf")}, headers=headers)
                resume_id = res.json().get("id") if res and res.status_code == 201 else None
        
        await test_endpoint(client, "List Resumes", "GET", "/resumes", headers=headers)
        if resume_id:
            await test_endpoint(client, "Get Resume", "GET", f"/resumes/{resume_id}", headers=headers)
        
        # Generate Ranking
        if job_id:
            await test_endpoint(client, "Generate Ranking", "POST", f"/rankings/generate/{job_id}", headers=headers)
            await asyncio.sleep(2)
            await test_endpoint(client, "Get Rankings", "GET", f"/rankings/{job_id}", headers=headers)
            if candidate_id:
                await test_endpoint(client, "Get Score Breakdown", "GET", f"/rankings/{job_id}/{candidate_id}", headers=headers)
                
        # AI Generation
        if candidate_id and job_id:
            res, _ = await test_endpoint(client, "Generate AI Artifacts", "POST", "/api/v1/ai/generate", json={"candidate_id": candidate_id, "job_id": job_id}, headers=headers)
            ai_job_id = res.json().get("job_id") if res and res.status_code == 202 else None
            
            if ai_job_id:
                for _ in range(15):
                    await asyncio.sleep(2)
                    res, _ = await test_endpoint(client, "Poll AI Job", "GET", f"/api/v1/ai/jobs/{ai_job_id}", headers=headers)
                    if res and res.json().get("status") in ["COMPLETED", "FAILED"]:
                        break
                
                await test_endpoint(client, "Get AI Summary", "GET", f"/api/v1/ai/summary/{candidate_id}/{job_id}", headers=headers)
                await test_endpoint(client, "Get AI Interview", "GET", f"/api/v1/ai/interview/{candidate_id}/{job_id}", headers=headers)
                await test_endpoint(client, "Get AI Skill Gap", "GET", f"/api/v1/ai/skill-gap/{candidate_id}/{job_id}", headers=headers)
        
        # Write report
        with open("full_qa_report.json", "w") as f:
            json.dump(REPORT, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
