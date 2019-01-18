import os
from flask import Flask, render_template, request, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "secret123string")

attempt = 0
score = 0
i = 0
wrong_answer = []
riddles = []
answers = []

def read_data():
    with open("data/riddles.txt", "r") as file:
        lines = file.read().splitlines()
    for n, text in enumerate(lines):
        if n%2 == 0:
            riddles.append(text)
        else:
            answers.append(text)

def process_answer(answer):
    global attempt
    global score
    global i
    if request.method == "POST":
        response = request.form["answer"]
        if response.lower() == answer and attempt == 0:
            flash("That's correct! You scored 5 points!")
            score += 5
            i += 1
        elif response.lower() != answer and attempt == 0:
            flash("Sorry, that's not right! Please try again")
            attempt += 1
            wrong_answer.append(response)
        elif response.lower() == answer and attempt == 1:
            flash("That's correct! You scored 3 points!")
            score += 3
            i += 1
            attempt = 0
            wrong_answer.pop()
        elif response.lower() != answer and attempt == 1:
            flash("Sorry, that's not right! Please try again")
            attempt += 1
            wrong_answer.append(response)
        elif response.lower() == answer and attempt == 2:
            flash("That's correct! You scored 1 point!")
            score += 1
            i += 1
            attempt = 0
            remove_wrong_answer()
        else:
            flash("Sorry, that's not right! You have no more attempts, please try the next riddle")
            i += 1
            attempt = 0
            remove_wrong_answer()

def remove_wrong_answer():
    wrong_answer.pop(1)
    wrong_answer.pop()
    
@app.route("/", methods = ["GET", "POST"])
def index():
    """Welcome / sign in page"""
    if request.method == "POST":
        session["username"] = request.form["username"]
    if "username" in session:
        return redirect(url_for("game", username = session["username"]))
    return render_template("index.html")

@app.route("/game/<username>", methods = ["GET", "POST"])
def game(username):
    """Main game page"""
    read_data()
    if i < len(riddles):
        answer = answers[i]
        process_answer(answer)
        return render_template("game.html", riddle = riddles[i], score = score, wrong_answer = wrong_answer)
    else:
        return redirect(url_for("leaderboard"))

@app.route("/leaderboard", methods = ["GET", "POST"])
def leaderboard():
    """Show leaderboard page"""
    if i >= len(riddles):
        flash("Game Complete! Find your score on the leaderboard")
    username = session["username"]
    scores = []
    scores.append((username, score))
    top_scores = sorted(scores, key = lambda e: e[1], reverse = True)
    return render_template("leaderboard.html", top_scores = top_scores)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host = os.getenv('IP'), port = int(os.getenv('PORT')), debug = True)