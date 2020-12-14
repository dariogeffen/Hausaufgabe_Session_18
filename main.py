from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db
import random, uuid, hashlib

app = Flask(__name__)
db.create_all()

@app.route("/", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/signed_up", methods=["POST"])
def signed_up():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    secret_number = random.randint(1, 30)

    user = db.query(User).filter_by(email=email).first()

    if not user:
        # create a User object
        session_token = str(uuid.uuid4())
        user = User(name=name, email=email, secret_number=secret_number, password=hashed_password, session_token=session_token)
        # save the user object into a database
        db.add(user)
        db.commit()
        response = make_response(redirect(url_for('game')))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')
        return response
    else:
        return "This user already exists, please log in to access your account."



@app.route("/logged_in", methods=["POST"])
def logged_in():
    email = request.form.get("user-email")
    password = request.form.get("user-password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    secret_number = random.randint(1, 30)
    user = db.query(User).filter_by(email=email).first()

    if not user:
        return "There is no registered user with this email address. Pleas go back and sign up first."
    if hashed_password != user.password:
        return "WRONG PASSWORD! Go back and try again."
    elif hashed_password == user.password:
        # create a random session token for this user
        session_token = str(uuid.uuid4())

    user.secret_number = secret_number
    user.session_token = session_token
    db.add(user)
    db.commit()

    name = user.name
    response = make_response(redirect(url_for('game')))
    response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')
    return response

@app.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "GET":
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token).first()
        name = user.name
        return render_template("index.html", name=name)
    elif request.method == "POST":
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token).first()
        name = user.name
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
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    new_secret = random.randint(1, 30)
    user.secret_number = new_secret
    db.add(user)
    db.commit()
    response = make_response(redirect(url_for('game')))
    return response


if __name__ == '__main__':
    app.run()  # if you use the port parameter, delete it before deploying to Heroku