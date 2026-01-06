from flask import Flask, render_template, request
from flask import send_file
import csv

app = Flask(__name__)

# Pilihan voting
options = {
    "1": "Setuju",
    "2": "Tidak Setuju",
    "3": "Abstain"
}

# Penyimpanan suara
votes = {
    "1": 0,
    "2": 0,
    "3": 0
}

@app.route("/", methods=["GET", "POST"])
def vote():
    message = ""

    if request.method == "POST":
        choice = request.form.get("vote")

        if choice in votes:
            votes[choice] += 1
            message = "✅ Vote berhasil disimpan"
        else:
            message = "❌ Pilihan tidak valid"

    return render_template(
        "vote.html",
        options=options,
        votes=votes,
        message=message
    )

@app.route("/export")
def export_csv():
    filename = "hasil_voting.csv"

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Pilihan", "Jumlah Suara"])
        for key, value in votes.items():
            writer.writerow([options[key], value])

    return send_file(filename, as_attachment=True)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
