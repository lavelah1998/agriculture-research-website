
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)

import sqlite3
import os
from werkzeug.utils import secure_filename
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
# CV upload configuration
app.config["UPLOAD_FOLDER"] = os.path.join(
    app.static_folder, "documents"
)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Application security settings
app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is required.")
)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise RuntimeError(
        "ADMIN_USERNAME and ADMIN_PASSWORD environment variables are required."
    )

ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)
)

# Database configuration
os.makedirs("instance", exist_ok=True)

DATABASE = os.path.join("instance", "agriculture_research.db")


# Database connection
def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Create database tables
def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            publication_type TEXT,
            journal TEXT,
            year INTEGER,
            doi TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            findings TEXT,
            status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            year INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# Protect administrator pages
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return wrapper


# Public homepage
@app.route("/")
def home():
    connection = get_connection()

    publications = connection.execute(
        "SELECT * FROM publications ORDER BY year DESC, id DESC"
    ).fetchall()

    projects = connection.execute(
        "SELECT * FROM research_projects ORDER BY id DESC"
    ).fetchall()

    achievements = connection.execute(
        "SELECT * FROM achievements ORDER BY year DESC, id DESC"
    ).fetchall()

    cv_files = [
        filename for filename in os.listdir(app.config["UPLOAD_FOLDER"])
        if filename.lower().endswith(".pdf")
    ]

    connection.close()

    return render_template(
        "index.html",
        publications=publications,
        projects=projects,
        achievements=achievements,
        cv_files=cv_files
    )


# Administrator login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if (
            username == ADMIN_USERNAME
            and check_password_hash(ADMIN_PASSWORD_HASH, password)
        ):
            session.clear()
            session["admin_logged_in"] = True

            flash("Login successful!", "success")

            return redirect(url_for("admin_dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


# Administrator dashboard
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM publications")
    publication_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM research_projects")
    project_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM achievements")
    achievement_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contact_messages")
    message_count = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        publication_count=publication_count,
        project_count=project_count,
        achievement_count=achievement_count,
        message_count=message_count
    )


# Administrator logout
@app.route("/admin/logout")
@login_required
def admin_logout():

    session.clear()

    flash("You have logged out successfully.", "success")

    return redirect(url_for("admin_login"))


# ==========================================
# PUBLICATION MANAGEMENT
# ==========================================

@app.route("/admin/publications")
@login_required
def admin_publications():

    connection = get_connection()

    publications = connection.execute(
        "SELECT * FROM publications ORDER BY year DESC, id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "publications.html",
        publications=publications
    )


@app.route("/admin/publications/add", methods=["POST"])
@login_required
def add_publication():

    title = request.form.get("title", "").strip()
    publication_type = request.form.get("publication_type", "").strip()
    journal = request.form.get("journal", "").strip()
    year = request.form.get("year", "").strip()
    doi = request.form.get("doi", "").strip()

    if not title:
        flash("Publication title is required.", "error")
        return redirect(url_for("admin_publications"))

    try:
        publication_year = int(year) if year else None
    except ValueError:
        flash("Please enter a valid publication year.", "error")
        return redirect(url_for("admin_publications"))

    connection = get_connection()

    connection.execute("""
        INSERT INTO publications
        (title, publication_type, journal, year, doi)
        VALUES (?, ?, ?, ?, ?)
    """, (title, publication_type, journal, publication_year, doi))

    connection.commit()
    connection.close()

    flash("Publication added successfully!", "success")

    return redirect(url_for("admin_publications"))


@app.route("/admin/publications/delete/<int:publication_id>", methods=["POST"])
@login_required
def delete_publication(publication_id):

    connection = get_connection()

    connection.execute(
        "DELETE FROM publications WHERE id = ?",
        (publication_id,)
    )

    connection.commit()
    connection.close()

    flash("Publication deleted successfully.", "success")

    return redirect(url_for("admin_publications"))

# ==========================================
# RESEARCH PROJECT MANAGEMENT
# ==========================================

@app.route("/admin/projects")
@login_required
def admin_projects():

    connection = get_connection()

    projects = connection.execute(
        "SELECT * FROM research_projects ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "projects.html",
        projects=projects
    )


@app.route("/admin/projects/add", methods=["POST"])
@login_required
def add_project():

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    findings = request.form.get("findings", "").strip()
    status = request.form.get("status", "").strip()

    if not title:
        flash("Project title is required.", "error")
        return redirect(url_for("admin_projects"))

    connection = get_connection()

    connection.execute("""
        INSERT INTO research_projects
        (title, description, findings, status)
        VALUES (?, ?, ?, ?)
    """, (title, description, findings, status))

    connection.commit()
    connection.close()

    flash("Research project added successfully!", "success")

    return redirect(url_for("admin_projects"))


@app.route("/admin/projects/delete/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):

    connection = get_connection()

    connection.execute(
        "DELETE FROM research_projects WHERE id = ?",
        (project_id,)
    )

    connection.commit()
    connection.close()

    flash("Research project deleted successfully.", "success")

    return redirect(url_for("admin_projects"))


# ==========================================
# ACADEMIC ACHIEVEMENTS MANAGEMENT
# ==========================================

@app.route("/admin/achievements")
@login_required
def admin_achievements():

    connection = get_connection()

    achievements = connection.execute(
        "SELECT * FROM achievements ORDER BY year DESC, id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "achievements.html",
        achievements=achievements
    )


@app.route("/admin/achievements/add", methods=["POST"])
@login_required
def add_achievement():

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    year = request.form.get("year", "").strip()

    if not title:
        flash("Achievement title is required.", "error")
        return redirect(url_for("admin_achievements"))

    try:
        achievement_year = int(year) if year else None
    except ValueError:
        flash("Please enter a valid year.", "error")
        return redirect(url_for("admin_achievements"))

    connection = get_connection()

    connection.execute("""
        INSERT INTO achievements (title, description, year)
        VALUES (?, ?, ?)
    """, (title, description, achievement_year))

    connection.commit()
    connection.close()

    flash("Achievement added successfully!", "success")

    return redirect(url_for("admin_achievements"))


@app.route("/admin/achievements/delete/<int:achievement_id>", methods=["POST"])
@login_required
def delete_achievement(achievement_id):

    connection = get_connection()

    connection.execute(
        "DELETE FROM achievements WHERE id = ?",
        (achievement_id,)
    )

    connection.commit()
    connection.close()

    flash("Achievement deleted successfully.", "success")

    return redirect(url_for("admin_achievements"))


# ==========================================
# CONTACT FORM AND MESSAGE MANAGEMENT
# ==========================================

@app.route("/contact", methods=["POST"])
def submit_contact():

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Please complete all required contact fields.", "error")
        return redirect(url_for("home"))

    connection = get_connection()

    connection.execute("""
        INSERT INTO contact_messages (name, email, subject, message)
        VALUES (?, ?, ?, ?)
    """, (name, email, subject, message))

    connection.commit()
    connection.close()

    flash("Your message has been submitted successfully.", "success")

    return redirect(url_for("home"))


@app.route("/admin/messages")
@login_required
def admin_messages():

    connection = get_connection()

    messages = connection.execute(
        "SELECT * FROM contact_messages ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "messages.html",
        messages=messages
    )


@app.route("/admin/messages/delete/<int:message_id>", methods=["POST"])
@login_required
def delete_message(message_id):

    connection = get_connection()

    connection.execute(
        "DELETE FROM contact_messages WHERE id = ?",
        (message_id,)
    )

    connection.commit()
    connection.close()

    flash("Message deleted successfully.", "success")

    return redirect(url_for("admin_messages"))



# ==========================================
# ACADEMIC CV UPLOAD
# ==========================================

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/admin/upload-cv", methods=["GET", "POST"])
@login_required
def upload_cv():

    if request.method == "POST":

        if "cv_file" not in request.files:
            flash("No file was selected.", "error")
            return redirect(url_for("upload_cv"))

        file = request.files["cv_file"]

        if file.filename == "":
            flash("Please select a PDF file.", "error")
            return redirect(url_for("upload_cv"))

        if not allowed_file(file.filename):
            flash("Only PDF files are allowed.", "error")
            return redirect(url_for("upload_cv"))

        filename = secure_filename(file.filename)

        if not filename:
            flash("Invalid filename.", "error")
            return redirect(url_for("upload_cv"))

        # Remove the previous CV when replacing it
        upload_folder = app.config["UPLOAD_FOLDER"]

        for old_file in os.listdir(upload_folder):
            if old_file.lower().endswith(".pdf"):
                os.remove(os.path.join(upload_folder, old_file))

        file.save(os.path.join(upload_folder, filename))

        flash("Academic CV uploaded successfully!", "success")

        return redirect(url_for("upload_cv"))

    cv_files = [
        filename for filename in os.listdir(app.config["UPLOAD_FOLDER"])
        if filename.lower().endswith(".pdf")
    ]

    return render_template("upload_cv.html", cv_files=cv_files)

# Initialize database
create_tables()


if __name__ == "__main__":
    app.run(debug=False)
