import spacy
from pdfminer.high_level import extract_text

nlp = spacy.load("en_core_web_sm")

def extract_resume_text(file_path):
    return extract_text(file_path)

def extract_skills(text):
    skills_list = ["python", "java", "sql", "machine learning", "html", "css", "javascript"]
    found = []

    for skill in skills_list:
        if skill in text.lower():
            found.append(skill)

    return found