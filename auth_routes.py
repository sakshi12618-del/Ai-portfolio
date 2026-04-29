from flask import Blueprint, render_template, request, redirect
from flask_login import login_user, logout_user, login_required
from models import db, User


auth = Blueprint('auth', __name__)


# ---------------- REGISTER ----------------
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            return "User already exists"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template("register.html")


# ---------------- LOGIN ----------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)   # ✅ FIX (NO STRING PASS)
            return redirect('/dashboard')

        return "Invalid credentials"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')