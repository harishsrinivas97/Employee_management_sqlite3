from flask import Flask, request, redirect, render_template,url_for,session,flash
import sqlite3
import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired,BadSignature
import re
import smtplib

app = Flask(__name__)
app.secret_key = "my-secret-key"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'   # Gmail SMTP server
app.config['MAIL_PORT'] = 587                 # Mail server port
app.config['MAIL_USE_TLS'] = True             # Use TLS encryption
app.config['MAIL_USERNAME'] = "22a31a4457@gmail.com"  # Sender email
app.config['MAIL_PASSWORD'] = "wohe dvoo gwdv ftgo"     # App Password from Gmail

mail = Mail(app)  # Initialize Flask-Mail with app

# Token Serializer (used for generating secure reset password links)
s = URLSafeTimedSerializer(app.secret_key)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "company.db")

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = None  # Keep query results as tuples, like the old MySQL code.
    return connection

@app.route('/')
def Home():
    return render_template('home.html')

# SIGNUP PAGE
@app.route('/register')
def Signup():
    return render_template("register.html")

#Login Page
@app.route('/login')
def Login():
    return render_template('login.html')

#about page
@app.route('/about')
def About():
    return render_template('about.html')

#add employees
@app.route('/add_employee')
def Add_Employee():
    return render_template('add_employee.html')

# View Employees
@app.route('/view_employees')
def View():
    if not session.get('logged_in'):
        flash("Please log in first.", "error")
        return redirect(url_for('Login'))

    manager_id = session['id']

    conn = get_db_connection()

    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM employee WHERE Manager_id = ?",
        (manager_id,)
    )
    result = cur.fetchall()
    cur.close()

    conn.close()
    return render_template('view_employee.html', employee=result)

#add employe to the databse
@app.route('/add_employee', methods=['GET', 'POST'])
def Add_employee():

    if not session.get('logged_in'):
        flash("Please log in first.", "error")
        return redirect(url_for('Login'))

    if request.method == 'POST':
        name = request.form['ename']
        dept = request.form['edept']
        salary = request.form['esalary']
        phone = request.form['ephone']
        manager_id = session['id']

        conn = get_db_connection()

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO employee
            (ename, edept, esalary, ephone, Manager_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name, dept, salary, phone, manager_id))

        conn.commit()
        cur.close()

        conn.close()
        flash("Employee added successfully!", "success")
        return redirect(url_for('Dashboard'))

    return render_template('add_employee.html')


# Dashboard
@app.route('/dashboard')
def Dashboard():
    if not session.get("logged_in"):
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for("Login"))

    email = session.get("email")

    conn = get_db_connection()

    cur = conn.cursor()
    cur.execute("SELECT name FROM users WHERE email = ?", (email,))
    result = cur.fetchone()
    cur.close()

    conn.close()
    name = result[0] if result else email

    return render_template('dashboard.html', name=name)


# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out successfully!", "success")
    return redirect(url_for("Home"))



#add Employee to the database
@app.route('/add_Manager', methods=['POST'])
def Add_Manager():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form.get('confirm_password')
    role = request.form['role']

    # Validation: Passwords must match
    if confirm_password and password != confirm_password:
        flash("Passwords do not match! Please try again.", "error")
        return redirect('/register')

    conn = get_db_connection()

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (name, email, password, role)
    )
    conn.commit()
    cur.close()

    conn.close()
    flash("You have registered successfully! Please log in.", "success")
    return redirect('/login')



# Verify Login
@app.route('/verify', methods=['GET', 'POST'])
def Verify():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()

        cur = conn.cursor()
        cur.execute(
            "SELECT id,password FROM users WHERE email = ?",
            (email,)
        )
        result = cur.fetchone()
        cur.close()

        conn.close()
        if result is None:
            flash("You are not registered! Please sign up first.", "error")
            return redirect('/login')

        if result[1] == password:
            session['email'] = email
            session['id']=result[0]
            session['logged_in'] = True
            flash("Login successful!", "success")
            return redirect('/dashboard')

        else:
            flash("Incorrect password or Email. Please try again.", "error")
            return redirect('/login')

    return redirect('/login')

#delete row in table
@app.route('/delete_employee/<int:id>')
def Delete(id):
    conn = get_db_connection()
    cur=conn.cursor()
    cur.execute("delete from employee where eid=?",(id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/view_employees')

#edit employee in table
@app.route('/edit_employee/<int:id>')
def Edit(id):
    if not session.get('logged_in'):
        flash("Please log in first.", "error")
        return redirect(url_for('Login'))
    conn = get_db_connection()
    cur=conn.cursor()
    cur.execute("select * from employee where eid=?",(id,))
    result=cur.fetchone()
    print(result)
    cur.close()
    conn.close()
    return render_template('edit_employee.html',employee=result)

#edit employee
@app.route('/edit_employee/<int:id>',methods=['post'])
def Edit_employee(id):
    if not session.get('logged_in'):
        flash("Please log in first.", "error")
        return redirect(url_for('Login'))
    name=request.form['ename']
    dept=request.form['edept']
    salary=request.form['esalary']
    phone=request.form['ephone']
    conn = get_db_connection()
    cur=conn.cursor()
    cur.execute("""update employee set ename=?,edept=?,esalary=?,ephone=? where eid=?""",
                (name,dept,salary,phone,id))
    conn.commit()
    cur.close()
    conn.close()
    flash("Employee updated successfully!", "success")
    return redirect('/view_employees')


# Forgot Password Page
@app.route('/forgot_password')
def forgot_password():
    return render_template("forgot_password.html")


# Sending Reset Password Email Link
@app.route('/send_reset_link', methods=['POST'])
def send_reset_link():
    email = request.form['email']

    # Check whether email exists in SQLite
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    cur.close()

    conn.close()
    if user is None:
        flash("Email not registered!")
        return redirect(url_for('forgot_password'))

    # Create secure token containing the email
    token = s.dumps(email, salt='password-reset-salt')

    # Generate reset link
    link = url_for('reset_password',token=token,_external=True)

    # Send email
    msg = Message(
    "Password Reset Request",
    sender=app.config['MAIL_USERNAME'],
    recipients=[email]
    
    )
    msg.body = f"Click this link to reset your password: {link}"
    mail.send(msg)

    flash("Reset link sent to your email!")
    return redirect(url_for('Login'))


# Reset Password Page
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(
            token,
            salt='password-reset-salt',
            max_age=300
        )
    except SignatureExpired:
        return "Link expired! Please request a new one."
    except BadSignature:
        return "Invalid reset link!"

    if request.method == 'POST':
        new_password = request.form['password']

        conn = get_db_connection()

        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (new_password, email)
        )
        conn.commit()
        cur.close()

        conn.close()
        flash("Password reset successful! Please log in.")
        return redirect(url_for('Login'))

    return render_template("reset_password.html")

def send_contact_email(name, email, subject, message_body):
    msg = Message(
        subject=f"[Contact Request] {subject}",
        sender=app.config['MAIL_USERNAME'],
        recipients=[app.config['MAIL_USERNAME']],
        reply_to=email
    )
    msg.body = f"From: {name} <{email}>\nSubject: {subject}\n\nMessage:\n{message_body}"
    mail.send(msg)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not all([name, email, subject, message]):
            flash("Please complete all fields.", "danger")
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email address.", "danger")
        else:
            try:
                send_contact_email(name, email, subject, message)
                flash("Your message has been sent successfully!", "success")
                return redirect(url_for("contact"))
            except (smtplib.SMTPException, OSError, RuntimeError) as error:
                app.logger.exception("Could not send contact email.")
                print("EMAIL ERROR:", repr(error))
                flash("Email could not be sent. Check the console for details.", "danger")

    return render_template("contact.html")


if __name__ == '__main__':
    app.run(debug=True)