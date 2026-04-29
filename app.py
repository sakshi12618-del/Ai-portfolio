from flask import Flask, render_template, request, redirect, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required
import os
from werkzeug.utils import secure_filename
from resume_parser import extract_resume_text, extract_skills
from scorer import calculate_score, suggest_roles, missing_skills
from models import db, User, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-change-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    # GET request - show upload form
    if request.method == "GET":
        return render_template("upload.html")
    
    # POST request - process file upload
    try:
        # Check if file is in request
        if "resume" not in request.files:
            return render_template("error.html", 
                                 error="No file uploaded. Please select a resume file.",
                                 back_url="/"), 400

        file = request.files["resume"]

        # Check if file is selected
        if file.filename == "":
            return render_template("error.html",
                                 error="No file selected. Please choose a resume file.",
                                 back_url="/"), 400

        # Check file extension
        if not allowed_file(file.filename):
            return render_template("error.html",
                                 error="Invalid file type. Please upload a PDF, DOC, DOCX, or TXT file.",
                                 back_url="/"), 400

        # Secure filename
        filename = secure_filename(file.filename)
        
        # Create unique filename to avoid overwrites
        import time
        filename = f"{int(time.time())}_{filename}"
        
        # Save file
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        # Extract text and skills
        text = extract_resume_text(path)
        
        if not text or text.strip() == "":
            return render_template("error.html",
                                 error="Could not extract text from resume. Please check the file format.",
                                 back_url="/"), 400

        skills = extract_skills(text)
        
        if not skills or len(skills) == 0:
            return render_template("error.html",
                                 error="No skills detected. Please ensure your resume contains relevant skill information.",
                                 back_url="/"), 400

        score = calculate_score(skills)
        role = suggest_roles(skills)
        missing = missing_skills(skills)

        # Clean up uploaded file
        try:
            os.remove(path)
        except:
            pass

        return render_template("result.html",
                               skills=skills,
                               score=score,
                               role=role,
                               missing=missing)

    except Exception as e:
        print(f"Error in analyze: {str(e)}")
        return render_template("error.html",
                             error=f"An error occurred while analyzing your resume. Please try again.",
                             back_url="/"), 500

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({"message": "Login successful", "success": True})
        return jsonify({"error": "Invalid credentials", "success": False}), 401
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"message": "User already exists", "success": False}), 400
        
        new_user = User(username=username, password=password)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Account created successfully", "success": True})
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)