# 🚀 Smart Hire Engine
### Resume Evaluation and Ranking System (RSART)

<p align="center">
  <a href="https://smart-hire-engine-resume-evaluation-and.onrender.com">
    <img src="https://img.shields.io/badge/Live%20Demo-Visit%20Project-2E8B57?style=for-the-badge" alt="Live Demo">
  </a>
  <a href="https://github.com/tejugowda-03/Smart-Hire-Engine-Resume-Evaluation-and-Ranking-System">
    <img src="https://img.shields.io/badge/GitHub-Source%20Code-181717?style=for-the-badge&logo=github" alt="GitHub">
  </a>
</p>

## 📌 Overview

Smart Hire Engine is a web-based application that simplifies resume screening using Natural Language Processing (NLP) and Machine Learning techniques. It compares candidate resumes with job descriptions, calculates similarity scores, and ranks candidates based on their relevance to job requirements.

## ✨ Key Features

- 🔐 User authentication with demo access.
- 📄 Resume upload and text extraction.
- 📋 Job description selection.
- 🧠 NLP-based resume processing.
- 📊 TF-IDF and cosine similarity matching.
- 🏆 Candidate scoring and ranking.
- 🎯 Top candidate shortlisting.
- ⬇️ Resume download functionality.

## ⚙️ How It Works

**Resume Upload → Text Extraction → Text Preprocessing → TF-IDF Vectorization → Cosine Similarity → Candidate Scoring → Candidate Ranking**

The system uses TF-IDF to convert text into numerical representations and cosine similarity to measure the textual relevance between resumes and job descriptions.

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Language | Python |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript |
| NLP | spaCy, NLTK |
| Machine Learning | Scikit-learn |
| Matching Algorithm | TF-IDF, Cosine Similarity |
| Resume Parsing | PyPDF2, docx2txt |
| Database | SQLite / PostgreSQL |
| Deployment | Render |

## 🚀 Installation and Setup

**1. Clone the repository**

```bash
git clone https://github.com/tejugowda-03/Smart-Hire-Engine-Resume-Evaluation-and-Ranking-System.git
```

**2. Navigate to the project folder**

```bash
cd Smart-Hire-Engine-Resume-Evaluation-and-Ranking-System
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file using `.env.example` as a reference. Set your own `SECRET_KEY` and `DATABASE_URL`.

**5. Run the application**

```bash
python run.py
```

Open **http://127.0.0.1:8000/** in your browser.

## 🔑 Demo Access

| Field | Credentials |
|---|---|
| Username | `admin` |
| Password | `root` |

*Shared demonstration credentials are provided for project evaluation. Use fictional sample resumes when testing.*

## 🔮 Future Enhancements

- Improved resume parsing accuracy.
- Advanced skill-based matching.
- Detailed candidate evaluation reports.
- Individual recruiter accounts and role-based access.
- Enhanced data security and resume management.

## 📌 Project Information

| Detail | Description |
|---|---|
| Project | Smart Hire Engine (RSART) |
| Version | 1.0.0 |
| Domain | Artificial Intelligence and Machine Learning |
| Project Type | Internship Showcase Project |
| Deployment | Render |

## 🔗 Project Links

- **Live Application:** https://smart-hire-engine-resume-evaluation-and.onrender.com
- **GitHub Repository:** https://github.com/tejugowda-03/Smart-Hire-Engine-Resume-Evaluation-and-Ranking-System

---

<p align="center">
  **Smart Hire Engine**
  <br>
  <i>Smarter Resume Screening Through NLP and Machine Learning.</i>
  <br><br>
  Developed with ❤️ using Python, Flask and Machine Learning.
</p>
