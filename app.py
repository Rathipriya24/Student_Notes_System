import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import mysql.connector

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="student_notes_db"
    )


@app.route("/")
def login():
    return render_template("index.html")
@app.route("/login", methods=["GET", "POST"])
def login_user():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT * FROM students
        WHERE email = %s AND password = %s
        """

        cursor.execute(query, (email, password))
        student = cursor.fetchone()

        cursor.close()
        connection.close()

        if student:
            session["student_id"] = student["id"]
            session["student_name"] = student["name"]

            return redirect(url_for("dashboard"))

        else:
            return "Invalid email or password!"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

@app.route("/view_notes")
def view_notes():

    if "student_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM notes WHERE status = 'Approved' ORDER BY upload_date DESC"

    cursor.execute(query)
    notes = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("view_notes.html", notes=notes)

@app.route("/download/<filename>")
def download_file(filename):

    if "student_id" not in session:
        return redirect(url_for("login"))

    return send_from_directory("uploads", filename, as_attachment=True)

@app.route("/upload", methods=["GET", "POST"])
def upload_notes():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        subject = request.form["subject"]
        semester = request.form["semester"]

        file = request.files["file"]

        if file:
            file.save("uploads/" + file.filename)
            connection = get_db_connection()
            cursor = connection.cursor()

            query = """
            INSERT INTO notes
            (title, subject, semester, filename, uploaded_by)
            VALUES (%s, %s, %s, %s, %s)
            """

            values = (
                title,
                subject,
                semester,
                file.filename,
                session["student_id"]
            )

            cursor.execute(query, values)
            connection.commit()

            cursor.close()
            connection.close()

            return "Notes uploaded successfully!"

    return render_template("upload.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        department = request.form["department"]
        semester = request.form["semester"]

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO students
        (name, email, password, department, semester)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (name, email, password, department, semester)

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        return "Registration successful!"

    return render_template("register.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if email == os.getenv("ADMIN_EMAIL") and password == os.getenv("ADMIN_PASSWORD"):
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        return "Invalid staff email or password"

    return render_template("admin.html")


@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    subject = request.args.get("subject", "").strip()

    if subject:
        cursor.execute(
            "SELECT * FROM notes WHERE status = 'Pending' AND subject LIKE %s ORDER BY upload_date DESC",
            ("%" + subject + "%",)
        )
    else:
        cursor.execute(
            "SELECT * FROM notes WHERE status = 'Pending' ORDER BY upload_date DESC"
        )

    notes = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) AS total FROM notes")
    total_notes = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS pending FROM notes WHERE status = 'Pending'")
    pending_notes = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) AS approved FROM notes WHERE status = 'Approved'")
    approved_notes = cursor.fetchone()["approved"]

    cursor.execute("SELECT COUNT(*) AS rejected FROM notes WHERE status = 'Rejected'")
    rejected_notes = cursor.fetchone()["rejected"]

    cursor.close()
    connection.close()

    return render_template(
        "admin_dashboard.html",
        notes=notes,
        total_notes=total_notes,
        pending_notes=pending_notes,
        approved_notes=approved_notes,
        rejected_notes=rejected_notes
    )

@app.route("/admin/approve/<int:note_id>", methods=["POST"])
def approve_note(note_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE notes SET status = 'Approved' WHERE id = %s",
        (note_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/reject/<int:note_id>", methods=["POST"])
def reject_note(note_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE notes SET status = 'Rejected' WHERE id = %s",
        (note_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True)