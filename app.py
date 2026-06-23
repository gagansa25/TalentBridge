from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root@1234'
app.config['MYSQL_DB'] = 'talentbridge'

# Upload Folder
app.config['UPLOAD_FOLDER'] = 'uploads'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        course = request.form['course']
        skills = request.form['skills']

        cur = mysql.connection.cursor()

        cur.execute("""
        INSERT INTO students(name,email,password,course,skills)
        VALUES(%s,%s,%s,%s,%s)
        """, (name, email, password, course, skills))

        mysql.connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM students WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cur.fetchone()

        cur.close()

        if user:
            return render_template('student_dashboard.html', user=user)

        return "Invalid Email or Password"

    return render_template('login.html')
@app.route('/upload_resume', methods=['POST'])
def upload_resume():

    file = request.files.get('resume')
    email = request.form.get('email')

    if not file:
        return "No file selected"

    filename = file.filename

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    if email:
        cur = mysql.connection.cursor()

        cur.execute(
            "UPDATE students SET resume=%s WHERE email=%s",
            (filename, email)
        )

        mysql.connection.commit()
        cur.close()

    return "Resume Uploaded Successfully ✅"

if __name__ == '__main__':
    app.run(debug=True)