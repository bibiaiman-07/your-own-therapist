from flask import Flask, render_template, request, redirect, url_for, session
from utils.therapy_questions import therapy_questions
from utils.nlp_utils import analyze_sentiment
from utils.helpers import generate_bot_reaction
from utils.mood_predictor import predict_mood
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ------------------ HOME ------------------
@app.route('/')
def home():
    return render_template('home.html')

# ------------------ ASSESSMENT ------------------
questions = [
    # Depression (6)
    "Have you felt down, depressed, or hopeless?",
    "Have you lost interest or pleasure in activities you usually enjoy?",
    "Have you experienced feelings of worthlessness or guilt?",
    "Have you had trouble concentrating on things like reading or watching TV?",
    "Have you had thoughts of self-harm or that you'd be better off dead?",
    "Have you been feeling tired or lacking energy?",
    # Anxiety (6)
    "Have you felt nervous, anxious, or on edge?",
    "Have you had trouble controlling your worries?",
    "Have you experienced sudden feelings of panic or terror?",
    "Have you found it difficult to relax?",
    "Have you been easily irritated or annoyed?",
    "Have you experienced physical symptoms like trembling, sweating, or rapid heartbeat?",
    # Bipolar Disorder (6)
    "Have you felt unusually excited or overconfident without a reason?",
    "Have you felt like you don’t need sleep and still feel energetic?",
    "Have your thoughts been racing or jumping from topic to topic quickly?",
    "Have you made big plans or taken big risks you normally wouldn’t?",
    "Have you had periods of extreme irritability or aggression?",
    "Have you had sudden mood shifts from happy to sad or vice versa?",
    # Eating Disorder (7)
    "Have you been overly concerned about your body weight or shape?",
    "Have you restricted food intake even when hungry?",
    "Have you engaged in binge eating episodes?",
    "Have you made yourself vomit or used laxatives to control your weight?",
    "Have you exercised excessively to control your weight?",
    "Have you felt guilty after eating?",
    "Have you avoided social situations due to eating concerns?"
]

@app.route('/assessment')
def show_assessment():
    return render_template('assessment.html', questions=questions)

@app.route('/submit_assessment', methods=['POST'])
def submit_assessment():
    answers = [int(request.form.get(f'q{i+1}', 0)) for i in range(25)]
    scores = {
        "Depression": sum(answers[0:6]),
        "Anxiety": sum(answers[6:12]),
        "Bipolar Disorder": sum(answers[12:18]),
        "Eating Disorder": sum(answers[18:25])
    }

    diagnosis = {}
    for disorder, score in scores.items():
        if score >= 12:
            diagnosis[disorder] = "High"
        elif score >= 6:
            diagnosis[disorder] = "Moderate"
        else:
            diagnosis[disorder] = "Low"

    top_disorder = max(scores, key=scores.get)

    disorder_info = {
        "Depression": "Depression is a mood disorder that causes persistent sadness, hopelessness, and loss of interest.",
        "Anxiety": "Anxiety disorders involve chronic fear or worry, often accompanied by restlessness and fatigue.",
        "Bipolar Disorder": "Bipolar disorder causes shifts in mood, energy, and activity levels from depressive lows to manic highs.",
        "Eating Disorder": "Eating disorders involve extreme focus on body weight and shape, affecting daily eating habits."
    }

    return render_template('diagnosis.html',
                           scores=scores,
                           diagnosis=diagnosis,
                           top_disorder=top_disorder,
                           disorder_info=disorder_info)

# ------------------ START THERAPY ------------------
@app.route('/start_therapy')
def start_therapy():
    session['current_session'] = 1
    session['current_question'] = 0
    session['therapy_answers'] = {}
    session['chat_history'] = []
    return redirect(url_for('chat_therapy'))

# ------------------ CHATBOT THERAPY ------------------
@app.route('/chat_therapy', methods=['GET', 'POST'])
def chat_therapy():
    session_num = session.get('current_session', 1)
    question_num = session.get('current_question', 0)
    therapy_answers = session.get('therapy_answers', {})
    chat_history = session.get('chat_history', [])

    questions_list = therapy_questions.get(f"session_{session_num}", [])

    if request.method == 'POST':
        user_reply = request.form['user_reply']
        mood = predict_mood(user_reply)
        sentiment = analyze_sentiment(user_reply)

        chat_history.append({"sender": "user", "text": user_reply, "mood": mood})

        reaction = generate_bot_reaction(user_reply, mood)
        chat_history.append({"sender": "bot", "text": reaction})

        key = f"session_{session_num}"
        if key not in therapy_answers:
            therapy_answers[key] = []
        therapy_answers[key].append({"reply": user_reply, "mood": mood, "sentiment": sentiment})

        question_num += 1

        if question_num >= len(questions_list):
            session_num += 1
            question_num = 0
            if session_num > 5:
                return redirect(url_for('therapy_summary'))

    session['current_session'] = session_num
    session['current_question'] = question_num
    session['therapy_answers'] = therapy_answers
    session['chat_history'] = chat_history

    next_question = therapy_questions.get(f"session_{session_num}", [])[question_num]

    return render_template('therapy_session.html',
                           session_num=session_num,
                           question_num=question_num + 1,
                           question=next_question,
                           chat_history=chat_history)

# ------------------ THERAPY SUMMARY ------------------
@app.route('/therapy_summary')
def therapy_summary():
    all_answers = session.get('therapy_answers', {})

    session_labels = []
    avg_sentiments = []

    for session_key, answers in all_answers.items():
        session_labels.append(session_key.replace('_', ' ').title())
        sentiments = [ans['sentiment']['compound'] for ans in answers if ans.get('sentiment')]
        avg = sum(sentiments) / len(sentiments) if sentiments else 0
        avg_sentiments.append(avg)

    plt.figure(figsize=(10, 5))
    plt.plot(session_labels, avg_sentiments, marker='o', linestyle='-', color='teal')
    plt.title("Average Sentiment Score per Session")
    plt.xlabel("Therapy Sessions")
    plt.ylabel("Average Sentiment (Compound Score)")
    plt.ylim(-1, 1)
    plt.grid(True)

    chart_path = 'static/sentiment_trend.png'
    plt.savefig(chart_path)
    plt.close()

    return render_template('therapy_summary.html',
                           all_answers=all_answers,
                           chart_path=chart_path)

if __name__ == '__main__':
    app.run(debug=True)
