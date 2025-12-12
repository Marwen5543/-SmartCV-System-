# 🚀 SmartCV System

**SmartCV** is an AI-powered application that automatically analyzes CVs and fills recruitment forms, saving HR professionals from manual data entry.  

---

## ✨ Features

- 🧑‍💼 **Personal Info Extraction:** Name, email, phone, LinkedIn, GitHub, address  
- 💼 **Professional Experience:** Extract roles, companies, dates, descriptions  
- 🎓 **Education:** Extract degrees, institutions, dates, fields  
- 🛠️ **Skills Detection:** Technical skills and competencies  
- 🌐 **Languages:** Detect languages and proficiency levels  
- 📜 **Certifications:** Extract certificates and issuing organizations  
- 🖼️ **OCR Support:** Handles PDF and image-based CVs using Tesseract  
- 🔄 **PDF Conversion:** Converts PDFs to images with Poppler  

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI  
- **Frontend:** Angular 16  
- **OCR Engine:** Tesseract OCR  
- **PDF Conversion:** Poppler  
- **Data Processing:** Python regex & text parsing  

---

## 📂 Project Structure

- `smartcv-worker/` – Python backend service for OCR and CV parsing  
- `smartcv-frontend/` – Angular frontend for uploading CVs and viewing extracted data  
- `Smart_CV/` – Spring Boot backend for managing CV data and APIs  

---

## ⚡ Getting Started

### Backend (Python)
1. Install dependencies:
```bash
pip install -r requirements.txt
Ensure Tesseract OCR is installed and update the path in main.py:

python
Copier le code
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
Run the FastAPI server:

bash
Copier le code
python main.py
Frontend (Angular)
Navigate to the frontend folder:

bash
Copier le code
cd smartcv-frontend
Install dependencies:

bash
Copier le code
npm install
Run the Angular dev server:

bash
Copier le code
ng serve
Open http://localhost:4200 in your browser.

🔍 How It Works
Upload a CV (PDF or image).

The backend extracts text using OCR and parses it.

Structured CV data is returned in JSON.

Recruiters can auto-fill forms or integrate with HR systems.

📋 Example Output
json
Copier le code
{
  "personalInfo": {
    "fullName": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+123456789",
    "linkedin": "https://linkedin.com/in/johndoe",
    "portfolio": "https://github.com/johndoe",
    "address": "Paris, France",
    "summary": "Experienced software engineer with expertise in AI and full-stack development."
  },
  "experiences": [
    {
      "position": "Software Engineer",
      "company": "TechCorp",
      "startDate": "2022-01",
      "endDate": "2024-06",
      "current": false,
      "description": "• Developed AI-powered applications..."
    }
  ],
  "education": [
    {
      "institution": "ESPRIT Engineering School",
      "degree": "BSc in Computer Science",
      "field": "Computer Science",
      "startDate": "2018",
      "endDate": "2022",
      "gpa": ""
    }
  ],
  "skills": [{"name": "Python"}, {"name": "Angular"}, {"name": "Machine Learning"}],
  "languages": [{"language": "English", "proficiency": "Professional"}],
  "certifications": [{"name": "AWS Certified Developer", "issuer": "Amazon", "date": ""}]
}
