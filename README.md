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
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
Run the FastAPI server:

bash
python main.py
Frontend (Angular)
Navigate to the frontend folder:

bash
cd smartcv-frontend
Install dependencies:

bash
npm install
Run the Angular dev server:

bash
Copier le code
ng serve
Open http://localhost:4200 in your browser.
