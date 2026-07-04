with open('scripts/e2e_validation.py', 'r') as f:
    content = f.read()

replacements = [
    ('"/api/v1/jobs"', '"/jobs"'),
    ('f"/api/v1/jobs', 'f"/jobs'),
    ('"/api/v1/candidates"', '"/candidates"'),
    ('f"/api/v1/candidates', 'f"/candidates'),
    ('"/api/v1/resumes/upload"', '"/resumes/upload"'),
    ('f"/api/v1/resumes', 'f"/resumes'),
    ('f"/api/v1/rankings', 'f"/rankings'),
    ('"/api/v1/jobs/status', '"/jobs/status')
]

for old, new in replacements:
    content = content.replace(old, new)

with open('scripts/e2e_validation.py', 'w') as f:
    f.write(content)
