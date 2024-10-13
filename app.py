import bcrypt
import secrets
from flask import Flask, render_template, request, redirect, session, flash, url_for
from database import DBManager

secret_key = secrets.token_hex(16)  # Generates a random 32-character hex string

app = Flask(__name__)
app.secret_key = secret_key

database = DBManager(host="localhost", user="root", password=None, database="deadlinedestroyer")

@app.route("/", methods=["GET",  "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Query the database for the user
        query = "SELECT password FROM users WHERE email = %s"
        result = database.query(query, (email,))  # Adjust based on your DBManager implementation

        if result:
            # Assuming result returns a list of tuples
            stored_password = result[0][0]  # Get the password from the result
            # Verify the password
            if bcrypt.checkpw(password.encode(), stored_password.encode()):
                # Store user information in session
                session['email'] = email
                flash("Login successful!", "success")
                return redirect("/dashboard")  # Redirect to a dashboard or home page after login
            else:
                flash("Incorrect password. Please try again.", "danger")
        else:
            flash("Username not found. Please try again.", "danger")

    return render_template("index.html")

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    # Check and create the 'users' table if it doesn't exist
    table_name = "users"
    schema = """
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255)
    """
    database.create_table(table_name, schema)

    if request.method == "POST":
        # Get form data
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validate that passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("sign_up"))

        # Check if the email already exists
        database.cursor.execute(f"SELECT * FROM {table_name} WHERE email = %s", (email,))
        existing_user = database.cursor.fetchone()

        if existing_user:
            flash("Email already exists! Please use another email.", "error")
        else:
            salt = bcrypt.gensalt()
            # # Hash the password with the salt
            hashed_password = bcrypt.hashpw(password.encode(), salt)
            # Insert the new user data into the database
            columns = ["full_name", "email", "password"]
            values = (full_name, email, hashed_password)
            database.insert_data(table_name, columns, values)
            flash("Account created successfully!", "success")

        return redirect(url_for("/"))

    return render_template("signUp.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)
        
