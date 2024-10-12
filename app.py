from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET",  "POST"])
def index():
    return render_template("index.html")

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    return render_template("signUp.html")


if __name__ == "__main__":
    app.run(debug=True)
        
