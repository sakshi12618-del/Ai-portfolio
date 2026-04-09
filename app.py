from flask import Flask, render_template, request
import os
from resume_parser import extract_resume_text, extract_skills
from scorer import calculate_score, suggest_roles, missing_skills

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["resume"]

    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        text = extract_resume_text(path)
        skills = extract_skills(text)

        score = calculate_score(skills)
        role = suggest_roles(skills)
        missing = missing_skills(skills)

        return render_template("result.html",
                               skills=skills,
                               score=score,
                               role=role,
                               missing=missing)

    return "Upload Error"

if __name__ == "__main__":
   import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)