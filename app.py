from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import csv
import os


# ======================
# KONFIGURASI APP
# ======================
app = Flask(__name__)
app.secret_key = "secret-key-voting"

# ======================
# DATABASE (PATH ABSOLUT)
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "voting.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Tabel users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        nama TEXT,
        npm TEXT,
        jurusan TEXT,
        has_voted INTEGER DEFAULT 0
    )
    """)

    # Tabel votes
    cur.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        option_id TEXT PRIMARY KEY,
        count INTEGER
    )
    """)

    for key in ["1", "2", "3"]:
        cur.execute(
            "INSERT OR IGNORE INTO votes (option_id, count) VALUES (?, ?)",
            (key, 0)
        )

    conn.commit()
    conn.close()

# ======================
# DATA VOTING
# ======================
options = {
    "1": "Setuju",
    "2": "Tidak Setuju",
    "3": "Abstain"
}

# ======================
# REGISTER USER
# ======================
@app.route("/register", methods=["GET", "POST"])
def register_user():
    error = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        nama = request.form.get("nama")
        npm = request.form.get("npm")
        jurusan = request.form.get("jurusan")

        if not username or not password or not nama or not npm or not jurusan:
            error = "Semua field wajib diisi"
        else:
            conn = get_db()
            cur = conn.cursor()

            cur.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cur.fetchone():
                error = "Username sudah terdaftar"
                conn.close()
            else:
                cur.execute(
                    "INSERT INTO users (username, password, nama, npm, jurusan) VALUES (?, ?, ?, ?, ?)",
                    (username, password, nama, npm, jurusan)
                )
                conn.commit()
                conn.close()
                return redirect("/")

    return render_template("register.html", error=error)

# ======================
# LOGIN USER
# ======================
@app.route("/", methods=["GET", "POST"])
def login_user():
    error = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # ======================
        # CEK ADMIN DULU
        # ======================
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["admin"] = True
            return redirect("/dashboard")

        # ======================
        # CEK USER BIASA
        # ======================
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session.clear()
            session["user"] = username
            return redirect("/vote")
        else:
            error = "Username atau password salah"

    return render_template("login.html", error=error)


# ======================
# VOTING USER
# ======================
@app.route("/vote", methods=["GET", "POST"])
def vote():
    if "user" not in session:
        return redirect("/")

    username = session["user"]
    message = ""

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    if request.method == "POST":
        if user["has_voted"] == 1:
            message = "❌ Anda sudah melakukan voting."
        else:
            choice = request.form.get("vote")
            if choice in options:
                cur.execute(
                    "UPDATE votes SET count = count + 1 WHERE option_id = ?",
                    (choice,)
                )
                cur.execute(
                    "UPDATE users SET has_voted = 1 WHERE username = ?",
                    (username,)
                )
                conn.commit()
                message = "✅ Vote berhasil disimpan."

    cur.execute("SELECT * FROM votes")
    rows = cur.fetchall()
    votes = {row["option_id"]: row["count"] for row in rows}

    conn.close()

    return render_template(
        "vote.html",
        options=options,
        votes=votes,
        message=message,
        user_data=user
    )

# ======================
# ADMIN LOGIN
# ======================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ======================
# ADMIN DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM votes")
    rows = cur.fetchall()
    conn.close()

    votes = {row["option_id"]: row["count"] for row in rows}

    return render_template(
        "admin_dashboard.html",
        options=options,
        votes=votes
    )

# ======================
# API
@app.route("/api/votes")
def api_votes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM votes")
    rows = cur.fetchall()
    conn.close()

    data = {
        "labels": [],
        "counts": []
    }

    for r in rows:
        data["labels"].append(options[r["option_id"]])
        data["counts"].append(r["count"])

    return data

# ======================
# EXPORT CSV
# ======================
@app.route("/export")
def export_csv():
    if not session.get("admin"):
        return redirect("/admin")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM votes")
    rows = cur.fetchall()
    conn.close()

    filename = "hasil_voting.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Pilihan", "Jumlah Suara"])
        for r in rows:
            writer.writerow([options[r["option_id"]], r["count"]])

    return send_file(filename, as_attachment=True)

# ======================
# RESET VOTING
# ======================
@app.route("/reset")
def reset_voting():
    if not session.get("admin"):
        return redirect("/admin")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE votes SET count = 0")
    cur.execute("UPDATE users SET has_voted = 0")
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ======================
# LOGOUT
# ======================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ======================
# RUN APP
# ======================
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
