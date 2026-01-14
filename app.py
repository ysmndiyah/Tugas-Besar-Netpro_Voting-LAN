from flask import Flask, render_template, request, redirect, session, send_file
import csv
import sqlite3


def get_db():
    conn = sqlite3.connect("voting.db")
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.secret_key = "secret-key-voting"

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        nama TEXT,
        npm TEXT,
        jurusan TEXT,
        has_voted INTEGER DEFAULT 0
    )
    """)

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

votes = {
    "1": 0,
    "2": 0,
    "3": 0
}

users_voted = set()
registered_users = {
    "username1": {
        "nama": "...",
        "npm": "...",
        "jurusan": "..."
    }
}



# ======================
# REGISTER USER
# ======================
@app.route("/register", methods=["GET", "POST"])
def register_user():
    error = ""

    if request.method == "POST":
        username = request.form.get("username")
        nama = request.form.get("nama")
        npm = request.form.get("npm")
        jurusan = request.form.get("jurusan")

        if not username or not nama or not npm or not jurusan:
            error = "Semua field wajib diisi"
        else:
            conn = get_db()
            cur = conn.cursor()

            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cur.fetchone():
                error = "Username sudah terdaftar"
            else:
                cur.execute(
                    "INSERT INTO users (username, nama, npm, jurusan) VALUES (?, ?, ?, ?)",
                    (username, nama, npm, jurusan)
                )
                conn.commit()
                conn.close()
                return redirect("/")

    return render_template("register.html", error=error)


# ======================
# ADMIN (HARDCODED)
# ======================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ======================
# LOGIN USER
# ======================
@app.route("/", methods=["GET", "POST"])
def login_user():
    error = ""

    if request.method == "POST":
        username = request.form.get("username")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/vote")
        else:
            error = "Username belum terdaftar"

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
            if choice in ["1", "2", "3"]:
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
    vote_rows = cur.fetchall()

    votes = {row["option_id"]: row["count"] for row in vote_rows}

    conn.close()

    return render_template(
        "vote.html",
        options=options,
        votes=votes,
        message=message,
        user_data=user
    )



# ======================
# LOGIN ADMIN
# ======================
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = ""
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/dashboard")
        else:
            error = "❌ Login admin gagal"

    return render_template("admin_login.html", error=error)

# ======================
# DASHBOARD ADMIN
# ======================
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    return render_template(
        "admin_dashboard.html",
        options=options,
        votes=votes
    )

# ======================
# EXPORT CSV (ADMIN)
# ======================
@app.route("/export")
def export_csv():
    if not session.get("admin"):
        return redirect("/admin")

    filename = "hasil_voting.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Pilihan", "Jumlah Suara"])
        for key, value in votes.items():
            writer.writerow([options[key], value])

    return send_file(filename, as_attachment=True)

# ======================
# RESET VOTING (ADMIN)
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

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
