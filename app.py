from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

# Load questions
with open("data/questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

ANSWERS_FILE = "data/answers.json"

def load_answers():
    if os.path.exists(ANSWERS_FILE):
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_answers(answers):
    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(answers, f, indent=2, ensure_ascii=False)

@app.route("/")
def index():
    subjects = list(QUESTIONS.keys())
    return render_template("index.html", subjects=subjects)

@app.route("/subject/<subject_name>")
def subject(subject_name):
    subject_data = QUESTIONS.get(subject_name, {})
    answers = load_answers()
    return render_template("subject.html", subject=subject_name, sections=subject_data, answers=answers)

@app.route("/ebook/<subject_name>")
def ebook(subject_name):
    subject_data = QUESTIONS.get(subject_name, {})
    answers = load_answers()
    return render_template("ebook.html", subject=subject_name, sections=subject_data, answers=answers)

@app.route("/api/save-answer", methods=["POST"])
def save_answer():
    data = request.json
    question = data.get("question")
    answer = data.get("answer")
    answers = load_answers()
    answers[question] = answer
    save_answers(answers)
    return jsonify({"status": "success"})

@app.route("/api/export/<subject_name>")
def export_subject(subject_name):
    subject_data = QUESTIONS.get(subject_name, {})
    answers = load_answers()
    export_data = {"subject": subject_name, "qa_pairs": []}
    for section, questions in subject_data.items():
        for q in questions:
            export_data["qa_pairs"].append({
                "section": section,
                "question": q,
                "answer": answers.get(q, "")
            })
    return jsonify(export_data)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)