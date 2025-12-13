from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pytesseract
import os
from pdf2image import convert_from_path
import re
import json
from datetime import datetime

# Tesseract configuration
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"
UPLOADS_DIR = r"C:\Files\SmartCV\Smart_CV\uploads"

app = FastAPI()

class CvRequest(BaseModel):
    fileName: str

def parse_date_from_text(date_str):
    """Convert 'Feb 2025', 'Jun 2024', etc. to '2025-02' format"""
    if not date_str or date_str.strip() == '':
        return ''
    
    try:
        # Handle formats like "Feb 2025", "June 2024", etc.
        date_str = date_str.strip()
        months = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        for month_name, month_num in months.items():
            if month_name in date_str.lower():
                year = re.search(r'20\d{2}', date_str)
                if year:
                    return f"{year.group()}-{month_num}"
        
        # If it's already in YYYY-MM format or just YYYY
        year_match = re.search(r'20\d{2}', date_str)
        if year_match:
            return year_match.group()
            
    except:
        pass
    
    return ''

def parse_cv_data(text):
    """Parse extracted text into structured CV data"""
    cv_data = {
        "personalInfo": {},
        "experiences": [],
        "education": [],
        "skills": [],
        "languages": [],
        "certifications": []
    }
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # ========== PERSONAL INFO ==========
    
    # Extract name (usually first line)
    if lines:
        potential_name = lines[0]
        if len(potential_name) < 100 and not any(x in potential_name.lower() for x in ['curriculum', 'resume', 'cv', 'page']):
            cv_data["personalInfo"]["fullName"] = potential_name
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        cv_data["personalInfo"]["email"] = emails[0]
    
    # Extract phone number
    phone_pattern = r'[\+]?[0-9]{1,4}[\s\-]?[0-9]{2,4}[\s\-]?[0-9]{3,4}[\s\-]?[0-9]{3,4}'
    phones = re.findall(phone_pattern, text)
    if phones:
        cv_data["personalInfo"]["phone"] = phones[0].strip()
    
    # Extract LinkedIn
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
    if linkedin:
        cv_data["personalInfo"]["linkedin"] = f"https://{linkedin[0]}" if not linkedin[0].startswith('http') else linkedin[0]
    
    # Extract GitHub
    github_pattern = r'github\.com/[\w-]+'
    github = re.findall(github_pattern, text, re.IGNORECASE)
    if github:
        cv_data["personalInfo"]["portfolio"] = f"https://{github[0]}" if not github[0].startswith('http') else github[0]
    
    # Extract location/address (look for common patterns like "City, Country")
    address_pattern = r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?,\s*[A-Z][a-z]+)'
    addresses = re.findall(address_pattern, text)
    if addresses:
        cv_data["personalInfo"]["address"] = addresses[0]
    
    # Extract Summary section
    summary_match = re.search(r'(?:SUMMARY|PROFILE|OBJECTIVE)\s*\n(.*?)(?=\n(?:TECHNICAL\s*SKILLS?|SKILLS?|EXPERIENCE|EDUCATION|PROFESSIONAL))', 
                             text, re.IGNORECASE | re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1).strip()
        # Clean up summary (remove excessive line breaks)
        summary_text = ' '.join(summary_text.split())
        cv_data["personalInfo"]["summary"] = summary_text
    
    # ========== SKILLS ==========
    
    # Look for Technical Skills section
    skills_match = re.search(r'(?:TECHNICAL\s*SKILLS?|SKILLS?|COMPETENCIES)\s*\n(.*?)(?=\n(?:PROFESSIONAL\s*EXPERIENCE|EXPERIENCE|EDUCATION|PROJECTS|\Z))', 
                            text, re.IGNORECASE | re.DOTALL)
    if skills_match:
        skills_text = skills_match.group(1)
        # Split by bullet points, commas, or newlines
        skills_raw = re.split(r'[•\n]', skills_text)
        for skill_line in skills_raw:
            # Each line might have "Category: skill1, skill2, skill3"
            if ':' in skill_line:
                # Extract skills after the colon
                skills_part = skill_line.split(':', 1)[1]
                skills = re.split(r',', skills_part)
                for s in skills:
                    s_clean = s.strip()
                    # Remove parenthetical info like (Eureka, Gateway)
                    s_clean = re.sub(r'\([^)]*\)', '', s_clean).strip()
                    if s_clean and len(s_clean) > 1 and len(s_clean) < 50:
                        cv_data["skills"].append({"name": s_clean})
            else:
                # Just a plain skill
                s_clean = skill_line.strip()
                s_clean = re.sub(r'\([^)]*\)', '', s_clean).strip()
                if s_clean and len(s_clean) > 2 and len(s_clean) < 50 and not s_clean.startswith('•'):
                    cv_data["skills"].append({"name": s_clean})
    
    # ========== PROFESSIONAL EXPERIENCE ==========
    
    exp_match = re.search(r'(?:PROFESSIONAL\s*EXPERIENCE|WORK\s*EXPERIENCE|EXPERIENCE)\s*\n(.*?)(?=\n(?:KEY\s*PROJECTS?|PROJECTS?|EDUCATION|CERTIFICATIONS?|\Z))', 
                         text, re.IGNORECASE | re.DOTALL)
    if exp_match:
        exp_text = exp_match.group(1)
        # Split by job entries (look for date ranges)
        # Pattern: "Position, Company – Location   Date – Date"
        job_pattern = r'([^\n]+?),\s*([^\n]+?)\s*–\s*([^\n]+?)\s+((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[^\n]+?)(?=\n•|\n[A-Z]|\Z)'
        jobs = re.finditer(job_pattern, exp_text, re.IGNORECASE)
        
        for job in jobs:
            position = job.group(1).strip()
            company = job.group(2).strip()
            location = job.group(3).strip()
            dates = job.group(4).strip()
            
            # Parse dates
            date_parts = re.split(r'[–—-]', dates)
            start_date = parse_date_from_text(date_parts[0].strip()) if date_parts else ''
            end_date = ''
            current = False
            
            if len(date_parts) > 1:
                end_text = date_parts[1].strip()
                if any(word in end_text.lower() for word in ['present', 'current', 'now']):
                    current = True
                else:
                    end_date = parse_date_from_text(end_text)
            
            # Extract description (bullet points after this job)
            job_end_pos = job.end()
            next_job_match = re.search(r'\n[A-Z][a-z]+.*?,\s*[A-Z]', exp_text[job_end_pos:])
            if next_job_match:
                desc_end = job_end_pos + next_job_match.start()
            else:
                desc_end = len(exp_text)
            
            description_text = exp_text[job_end_pos:desc_end]
            # Get bullet points
            bullets = re.findall(r'•\s*([^\n•]+)', description_text)
            description = '\n'.join([f"• {b.strip()}" for b in bullets if b.strip()])
            
            experience = {
                "position": position,
                "company": company,
                "startDate": start_date,
                "endDate": end_date,
                "current": current,
                "description": description
            }
            cv_data["experiences"].append(experience)
    
    # ========== PROJECTS ==========
    # If no experience found or need more, check Projects section
    if len(cv_data["experiences"]) == 0:
        projects_match = re.search(r'(?:KEY\s*PROJECTS?|PROJECTS?)\s*\n(.*?)(?=\n(?:EDUCATION|CERTIFICATIONS?|\Z))', 
                                  text, re.IGNORECASE | re.DOTALL)
        if projects_match:
            projects_text = projects_match.group(1)
            project_pattern = r'([^\n]+?)\s+(?:GitHub|Oct|Nov|Dec|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep).*?\n(.*?)(?=\n[A-Z][^\n]+(?:GitHub|Oct|Nov|Dec)|\Z)'
            projects = re.finditer(project_pattern, projects_text, re.IGNORECASE | re.DOTALL)
            
            for proj in projects:
                project_name = proj.group(1).strip()
                description_text = proj.group(2).strip()
                bullets = re.findall(r'•\s*([^\n•]+)', description_text)
                description = '\n'.join([f"• {b.strip()}" for b in bullets if b.strip()])
                
                experience = {
                    "position": "Project",
                    "company": project_name,
                    "startDate": "",
                    "endDate": "",
                    "current": False,
                    "description": description
                }
                cv_data["experiences"].append(experience)
    
    # ========== EDUCATION ==========
    
    edu_match = re.search(r'(?:EDUCATION|ACADEMIC)\s*(?:&\s*CERTIFICATES?)?\s*\n(.*?)(?=\n(?:CERTIFICATES?|CERTIFICATIONS?|$))', 
                         text, re.IGNORECASE | re.DOTALL)
    if edu_match:
        edu_text = edu_match.group(1)
        
        # Pattern: Institution, Degree, Dates
        lines_edu = [l.strip() for l in edu_text.split('\n') if l.strip() and not l.strip().startswith('Certificates:')]
        
        # Group lines into education entries
        i = 0
        while i < len(lines_edu):
            if len(lines_edu[i]) > 3 and not any(x in lines_edu[i].lower() for x in ['certificates', 'certificate:']):
                institution = lines_edu[i]
                degree = lines_edu[i+1] if i+1 < len(lines_edu) else ''
                dates = lines_edu[i+2] if i+2 < len(lines_edu) else ''
                
                # Parse dates from the date line
                date_pattern = r'(20\d{2})\s*[–—-]\s*(20\d{2}|Present)'
                date_match = re.search(date_pattern, dates)
                start_date = ''
                end_date = ''
                
                if date_match:
                    start_date = date_match.group(1)
                    end_year = date_match.group(2)
                    end_date = end_year if end_year != 'Present' else ''
                
                # Determine field from degree
                field = ''
                if 'computer science' in degree.lower():
                    field = 'Computer Science'
                elif 'engineering' in degree.lower():
                    field = 'Engineering'
                
                education = {
                    "institution": institution,
                    "degree": degree,
                    "field": field,
                    "startDate": start_date,
                    "endDate": end_date,
                    "gpa": ""
                }
                cv_data["education"].append(education)
                i += 3
            else:
                i += 1
    
    # ========== CERTIFICATIONS ==========
    
    cert_match = re.search(r'(?:CERTIFICATES?|CERTIFICATIONS?)\s*:?\s*([^\n]+)', 
                          text, re.IGNORECASE)
    if cert_match:
        cert_text = cert_match.group(1)
        # Split by bullet points or common separators
        certs = re.split(r'[•\|]', cert_text)
        for cert in certs:
            cert_clean = cert.strip()
            if cert_clean and len(cert_clean) > 3:
                # Try to extract issuer if in format "Name (Issuer)"
                issuer = ''
                name = cert_clean
                
                issuer_match = re.search(r'\(([^)]+)\)', cert_clean)
                if issuer_match:
                    issuer = issuer_match.group(1)
                    name = cert_clean[:issuer_match.start()].strip()
                
                certification = {
                    "name": name,
                    "issuer": issuer,
                    "date": ""
                }
                cv_data["certifications"].append(certification)
    
    # ========== LANGUAGES ==========
    # Look for languages section or common language indicators
    lang_patterns = [
        r'(?:LANGUAGES?)\s*:?\s*(.*?)(?=\n\n|\n[A-Z][A-Z]|\Z)',
        r'(?:English|French|Arabic|Spanish|German|Chinese|Japanese)(?:\s*[:\-–]\s*|\s+)(Native|Fluent|Professional|Intermediate|Basic|Bilingual)',
    ]
    
    for pattern in lang_patterns:
        lang_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if lang_match:
            lang_text = lang_match.group(0) if lang_match.lastindex is None else lang_match.group(1)
            
            # Extract language-proficiency pairs
            lang_pair_pattern = r'(English|French|Arabic|Spanish|German|Chinese|Japanese|Italian|Portuguese|Russian|Korean|Hindi|Turkish)(?:\s*[:\-–]\s*|\s+)(Native|Fluent|Professional|Intermediate|Basic|Bilingual|Advanced|Beginner)'
            lang_pairs = re.finditer(lang_pair_pattern, lang_text, re.IGNORECASE)
            
            for pair in lang_pairs:
                language = {
                    "language": pair.group(1).capitalize(),
                    "proficiency": pair.group(2).capitalize()
                }
                # Avoid duplicates
                if not any(l["language"].lower() == language["language"].lower() for l in cv_data["languages"]):
                    cv_data["languages"].append(language)
            
            if len(cv_data["languages"]) > 0:
                break
    
    # If still no languages, look for common language mentions
    if len(cv_data["languages"]) == 0:
        common_langs = ['English', 'French', 'Arabic', 'Spanish', 'German']
        for lang in common_langs:
            if re.search(rf'\b{lang}\b', text, re.IGNORECASE):
                cv_data["languages"].append({
                    "language": lang,
                    "proficiency": "Professional"
                })
    
    return cv_data

@app.get("/")
def home():
    return {"message": "Python Worker is running!"}

@app.post("/extract")
def extract_text(request: CvRequest):
    file_path = os.path.join(UPLOADS_DIR, request.fileName)
    
    print(f"=== DEBUG INFO ===")
    print(f"Full path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            print("Converting PDF to images...")
            images = convert_from_path(
                file_path, 
                dpi=300,
                poppler_path=POPPLER_PATH
            )
            
            print(f"PDF converted to {len(images)} page(s)")
            
            all_text = []
            for i, image in enumerate(images):
                print(f"Processing page {i+1}/{len(images)}...")
                text = pytesseract.image_to_string(image, lang='eng')
                all_text.append(text)
            
            final_text = "\n\n".join(all_text)
            print(f"✅ Extracted {len(final_text)} characters from PDF")
            
            # Parse the extracted text into structured data
            cv_data = parse_cv_data(final_text)
            print(f"📋 Parsed CV data: {json.dumps(cv_data, indent=2)}")
            
            return {
                "fileName": request.fileName, 
                "text": final_text.strip(),
                "cvData": cv_data
            }
        
        else:
            text = pytesseract.image_to_string(file_path, lang='eng')
            cv_data = parse_cv_data(text)
            return {
                "fileName": request.fileName, 
                "text": text.strip(),
                "cvData": cv_data
            }
            
    except Exception as e:
        print(f"❌ OCR Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)