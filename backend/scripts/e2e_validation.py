import asyncio
import httpx
import json
import time
from uuid import uuid4
import jwt

API_BASE_URL = "http://localhost:8000"
RESUME_PATH = r"D:\Projects\AI-Recruitment-System\tests\fixtures\resumes\sample_resume.pdf"
JD_PATH = r"D:\Projects\AI-Recruitment-System\tests\fixtures\job_descriptions\JPD26.txt"
QA_REPORT_PATH = r"D:\Projects\AI-Recruitment-System\backend\qa_report.json"

REPORT_DATA = []

def log_report(title, success, details=None, execution_time=None):
    REPORT_DATA.append({
        "title": title,
        "success": success,
        "details": details,
        "execution_time": execution_time
    })
    print(f"[{'PASS' if success else 'FAIL'}] {title} (Time: {execution_time}s)" if execution_time else f"[{'PASS' if success else 'FAIL'}] {title}")
    if not success and details:
        print(f"   -> Error details: {details}")

async def main():
    print("Testing against running Uvicorn and Celery...")
    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=60.0) as client:
            
            # 1. Health Check
            t0 = time.time()
            res = await client.get("/health")
            log_report("Health Check", res.status_code == 200, res.text, time.time() - t0)
            
            # 2. Authentication
            t0 = time.time()
            user_email = f"qa_{uuid4()}@example.com"
            reg_res = await client.post("/api/v1/auth/register", json={"name": "QA Tester", "email": user_email, "password": "password123"})
            if reg_res.status_code != 201:
                print(f"Registration failed: {reg_res.text}")
            res = await client.post("/api/v1/auth/login", json={"email": user_email, "password": "password123"})
            auth_data = res.json() if res.status_code == 200 else {}
            token = auth_data.get("access_token")
            log_report("Authentication", res.status_code == 200 and token is not None, res.text, time.time() - t0)
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 3. Create Job
            t0 = time.time()
            with open(JD_PATH, "r", encoding="utf-8") as f:
                jd_text = f.read()
            
            decoded = jwt.decode(token, options={"verify_signature": False}) if token else {}
            user_id = decoded.get("sub")
            
            job_payload = {
                "title": "Data Scientist",
                "description": jd_text,
                "recruiter_id": user_id,
                "experience_required": 3,
                "education_required": "Master"
            }
            res = await client.post("/jobs", json=job_payload, headers=headers)
            job_id = res.json().get("job_id") if res.status_code == 201 else None
            log_report("Create Job with JPD26", res.status_code == 201, res.text, time.time() - t0)
            
            if not job_id:
                print("Failed to create job, stopping early.")
                return

            # 4. Create Candidate
            t0 = time.time()
            res = await client.post("/candidates", json={"full_name": "QA Candidate", "email": f"cand_{uuid4()}@example.com"}, headers=headers)
            candidate_id = res.json().get("candidate_id") if res.status_code == 201 else None
            log_report("Create Candidate", res.status_code == 201, res.text, time.time() - t0)
            
            if not candidate_id:
                print("Failed to create candidate, stopping early.")
                return

            # 5. Upload Resume
            t0 = time.time()
            with open(RESUME_PATH, "rb") as f:
                files = {"file": ("sample_resume.pdf", f, "application/pdf")}
                data = {"candidate_id": candidate_id}
                res = await client.post("/resumes/upload", data=data, files=files, headers=headers)
            resume_id = res.json().get("resume_id") if res.status_code == 202 else None
            log_report("Upload Resume", res.status_code == 202, res.text, time.time() - t0)
            
            # 6. Verify Resume Parsing
            t0 = time.time()
            parsed = False
            for _ in range(15):
                res = await client.get(f"/resumes/{resume_id}", headers=headers)
                if res.status_code == 200 and res.json().get("parsing_status") == "COMPLETED":
                    parsed = True
                    break
                elif res.status_code == 200 and res.json().get("parsing_status") == "FAILED":
                    break
                await asyncio.sleep(2)
            log_report("Resume Parsing (Celery)", parsed, res.text, time.time() - t0)
            
            # 7. Generate Ranking
            t0 = time.time()
            res = await client.post(f"/rankings/generate/{job_id}", headers=headers)
            log_report("Trigger Ranking Generation", res.status_code == 202, res.text, time.time() - t0)
            
            # Verify Ranking
            t0 = time.time()
            ranked = False
            for _ in range(15):
                res = await client.get(f"/rankings/{job_id}", headers=headers)
                if res.status_code == 200 and len(res.json()) > 0:
                    ranked = True
                    break
                await asyncio.sleep(2)
            log_report("Verify Ranking (Celery)", ranked, res.text, time.time() - t0)
            
            # 8. Trigger AI Generation
            t0 = time.time()
            res = await client.post("/api/v1/ai/generate", json={"candidate_id": candidate_id, "job_id": job_id}, headers=headers)
            ai_job_id = res.json().get("job_id") if res.status_code == 202 else None
            log_report("Trigger AI Generation", res.status_code == 202, res.text, time.time() - t0)
            
            # 9. Poll AI Generation
            t0 = time.time()
            completed = False
            statuses = []
            for _ in range(30):
                res = await client.get(f"/api/v1/ai/jobs/{ai_job_id}", headers=headers)
                if res.status_code == 200:
                    status = res.json().get("status")
                    if status not in statuses:
                        statuses.append(status)
                    if status == "COMPLETED":
                        completed = True
                        break
                    if status == "FAILED":
                        break
                await asyncio.sleep(2)
            log_report("Poll AI Generation (Celery)", completed, {"final_status": status if res.status_code == 200 else "error", "transitions": statuses}, time.time() - t0)
            
            # 10. Retrieve Summaries
            t0 = time.time()
            res = await client.get(f"/api/v1/ai/summary/{candidate_id}/{job_id}", headers=headers)
            log_report("Retrieve Summary", res.status_code == 200, res.text, time.time() - t0)
            
            t0 = time.time()
            res = await client.get(f"/api/v1/ai/interview/{candidate_id}/{job_id}", headers=headers)
            log_report("Retrieve Interview Questions", res.status_code == 200, res.text, time.time() - t0)
            
            t0 = time.time()
            res = await client.get(f"/api/v1/ai/skill-gap/{candidate_id}/{job_id}", headers=headers)
            log_report("Retrieve Skill Gap", res.status_code == 200, res.text, time.time() - t0)

            # Negative Testing
            res = await client.post("/api/v1/ai/generate", json={"candidate_id": candidate_id, "job_id": job_id})
            log_report("Negative: Missing JWT", res.status_code == 401, res.text)
            
            res = await client.post("/api/v1/ai/generate", json={"candidate_id": "invalid-uuid", "job_id": job_id}, headers=headers)
            log_report("Negative: Invalid UUID", res.status_code == 422, res.text)
            
            res = await client.post("/api/v1/ai/generate", json={"candidate_id": str(uuid4()), "job_id": job_id}, headers=headers)
            log_report("Negative: Unknown Candidate", res.status_code == 404, res.text)
            
            res = await client.post("/api/v1/ai/generate", json={"candidate_id": candidate_id, "job_id": job_id}, headers=headers)
            log_report("Negative: Idempotency", res.status_code == 202 and res.json().get("status") == "COMPLETED", res.text)

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"Writing QA report to {QA_REPORT_PATH}")
        with open(QA_REPORT_PATH, "w") as f:
            json.dump(REPORT_DATA, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
