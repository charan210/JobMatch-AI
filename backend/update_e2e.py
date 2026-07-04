with open('scripts/e2e_validation.py', 'r') as f:
    content = f.read()

replacements = [
    ('"/jobs"', '"/api/v1/jobs"'),
    ('f"/jobs', 'f"/api/v1/jobs'),
    ('"/candidates"', '"/api/v1/candidates"'),
    ('f"/candidates', 'f"/api/v1/candidates'),
    ('"/resumes/upload"', '"/api/v1/resumes/upload"'),
    ('f"/resumes', 'f"/api/v1/resumes'),
    ('f"/rankings', 'f"/api/v1/rankings'),
    ('"/jobs/status', '"/api/v1/jobs/status')
]
for old, new in replacements:
    content = content.replace(old, new)
with open('scripts/e2e_validation.py', 'w') as f:
    f.write(content)
