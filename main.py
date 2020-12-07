from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db
import random

app = Flask(__name__)
db.create_all()

@app.route("/", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/logged_in", methods=["POST"])
def logged_in():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    secret_number = random.randint(1, 30)

    user = User(name=name, email=email,secret_number=secret_number)

    db.add(user)
    db.commit()
    response = make_response(redirect(url_for('game')))
    response.set_cookie("email", email)
    response.set_cookie("name", name)
    return response

@app.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "GET":
        name = request.cookies.get("name")
        return render_template("index.html", name=name)
    elif request.method == "POST":
        email_address = request.cookies.get("email")
        name = request.cookies.get("name")
        user = db.query(User).filter_by(email=email_address).first()
        secret = str(user.secret_number)
        guess = str(request.form.get("number"))
        if guess == secret:
            response = make_response(render_template("success.html", number=guess, name=name))
            response.set_cookie("last_guess", guess)
            return response
        elif int(guess) > int(secret):
            indication = "smaller"
            response = make_response(render_template("index.html", compare=indication, number=guess))
            response.set_cookie("last_guess", guess)
            response.set_cookie("indication", indication)
            return response
        elif int(guess) < int(secret):
            indication = "bigger"
            response = make_response(render_template("index.html", compare=indication, number=guess))
            response.set_cookie("last_guess", guess)
            response.set_cookie("indication", indication)
            return response

@app.route("/success", methods=["GET", "POST"])
def success(guess):
    response = make_response(render_template("success.html", number=guess))
    return response

@app.route("/newgame", methods=["GET", "POST"])
def newgame():
    email_address = request.cookies.get("email")
    user = db.query(User).filter_by(email=email_address).first()
    new_secret = random.randint(1, 30)
    user.secret_number = new_secret
    db.add(user)
    db.commit()
    response = make_response(redirect(url_for('game')))
    return response


if __name__ == '__main__':
    app.run()  # if you use the port parameter, delete it before deploying to Heroku