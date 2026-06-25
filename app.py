
from flask import Flask, render_template, request, redirect, send_from_directory
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

# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Register
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


# Login
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
            return render_template(
                'student_dashboard.html',
                user=user
            )

        return "Invalid Email or Password"

    return render_template('login.html')


# Upload Resume
@app.route('/upload_resume', methods=['POST'])
def upload_resume():

    file = request.files.get('resume')
    email = request.form.get('email')

    if not file:
        return "No file selected"

    filename = file.filename

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    file.save(
        os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )
    )

    if email:
        cur = mysql.connection.cursor()

        cur.execute(
            "UPDATE students SET resume=%s WHERE email=%s",
            (filename, email)
        )

        mysql.connection.commit()
        cur.close()

    return "Resume Uploaded Successfully ✅"


# Add Job
@app.route('/add_job', methods=['GET', 'POST'])
def add_job():

    if request.method == 'POST':

        company_name = request.form['company_name']
        job_title = request.form['job_title']
        job_description = request.form['job_description']
        location = request.form['location']
        salary = request.form['salary']
        deadline = request.form['deadline']

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO jobs
            (company_name, job_title, job_description,
             location, salary, deadline)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            company_name,
            job_title,
            job_description,
            location,
            salary,
            deadline
        ))

        mysql.connection.commit()
        cur.close()

        return redirect('/jobs')

    return render_template('add_job.html')


# View Jobs
@app.route('/jobs')
def jobs():

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM jobs
        ORDER BY id DESC
    """)

    jobs = cur.fetchall()

    cur.close()

    return render_template(
        'jobs.html',
        jobs=jobs
    )
@app.route('/apply_job/<int:job_id>')
def apply_job(job_id):

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM jobs WHERE id=%s",
        (job_id,)
    )

    job = cur.fetchone()

    if job:

        company_name = job[1]
        job_title = job[2]

        student_email = "student@example.com"

        cur.execute("""
            INSERT INTO applications
            (student_email, company_name, job_title)
            VALUES (%s,%s,%s)
        """, (
            student_email,
            company_name,
            job_title
        ))

        mysql.connection.commit()

    cur.close()

    return redirect('/jobs')
@app.route('/my_applications')
def my_applications():

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM applications ORDER BY applied_at DESC"
    )

    applications = cur.fetchall()

    cur.close()

    return render_template(
        'my_applications.html',
        applications=applications
    )
@app.route('/admin_login', methods=['GET','POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username,password)
        )

        admin = cur.fetchone()

        cur.close()

        if admin:
            return redirect('/admin_dashboard')

        return "Invalid Admin Credentials"

    return render_template('admin_login.html')
@app.route('/admin_dashboard')
def admin_dashboard():

    cur = mysql.connection.cursor()

    # Total Students
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    # Total Jobs
    cur.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cur.fetchone()[0]

    # Total Applications
    cur.execute("SELECT COUNT(*) FROM applications")
    total_applications = cur.fetchone()[0]

    # Total Companies
    cur.execute("SELECT COUNT(*) FROM companies")
    total_companies = cur.fetchone()[0]

    # Placed Students
    cur.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE placement_status='Placed'
    """)
    placed_students = cur.fetchone()[0]

    # Not Placed Students
    cur.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE placement_status='Not Placed'
    """)
    not_placed_students = cur.fetchone()[0]

    cur.close()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_jobs=total_jobs,
        total_applications=total_applications,
        total_companies=total_companies,
        placed_students=placed_students,
        not_placed_students=not_placed_students
    )
@app.route('/manage_students')
def manage_students():

    search = request.args.get('search')

    cur = mysql.connection.cursor()

    if search:

        cur.execute("""
            SELECT *
            FROM students
            WHERE name LIKE %s
            OR email LIKE %s
        """, (
            '%' + search + '%',
            '%' + search + '%'
        ))

    else:

        cur.execute("SELECT * FROM students")

    students = cur.fetchall()

    cur.close()

    return render_template(
        'manage_students.html',
        students=students
    )
@app.route('/profile/<email>')
def profile(email):

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM students WHERE email=%s",
        (email,)
    )

    user = cur.fetchone()

    cur.close()

    return render_template(
        'profile.html',
        user=user
    )
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )
@app.route('/manage_jobs')
def manage_jobs():

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM jobs
        ORDER BY id DESC
    """)

    jobs = cur.fetchall()

    cur.close()

    return render_template(
        'manage_jobs.html',
        jobs=jobs
    )
@app.route('/delete_job/<int:id>')
def delete_job(id):

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM jobs WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    return redirect('/manage_jobs')
@app.route('/view_applications')
def view_applications():

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM applications
        ORDER BY applied_at DESC
    """)

    applications = cur.fetchall()

    cur.close()

    return render_template(
        'view_applications.html',
        applications=applications
    )
@app.route('/delete_application/<int:id>')
def delete_application(id):

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM applications WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    return redirect('/view_applications')
@app.route('/company_register', methods=['GET','POST'])
def company_register():

    if request.method == 'POST':

        company_name = request.form['company_name']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO companies
            (company_name,email,password)
            VALUES(%s,%s,%s)
        """, (
            company_name,
            email,
            password
        ))

        mysql.connection.commit()

        cur.close() 

        return redirect('/company_login')

    return render_template(
        'company_register.html'
    )
@app.route('/company_login', methods=['GET', 'POST'])
def company_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        # Company Login
        cur.execute(
            "SELECT * FROM companies WHERE email=%s AND password=%s",
            (email, password)
        )

        company = cur.fetchone()

        if company:

            # Total Jobs Posted by this Company
            cur.execute(
                "SELECT COUNT(*) FROM jobs WHERE company_name=%s",
                (company[1],)
            )
            total_jobs = cur.fetchone()[0]

            # Total Applications for this Company
            cur.execute(
                "SELECT COUNT(*) FROM applications WHERE company_name=%s",
                (company[1],)
            )
            total_applications = cur.fetchone()[0]

            # Recent Jobs
            cur.execute("""
                SELECT *
                FROM jobs
                WHERE company_name=%s
                ORDER BY id DESC
                LIMIT 5
            """, (company[1],))

            recent_jobs = cur.fetchall()

            # Recent Applicants
            cur.execute("""
                SELECT *
                FROM applications
                WHERE company_name=%s
                ORDER BY applied_at DESC
                LIMIT 5
            """, (company[1],))

            recent_applications = cur.fetchall()

            cur.close()

            return render_template(
                'company_dashboard.html',
                company=company,
                total_jobs=total_jobs,
                total_applications=total_applications,
                recent_jobs=recent_jobs,
                recent_applications=recent_applications
            )

        cur.close()

        return "Invalid Credentials"

    return render_template('company_login.html')

@app.route('/manage_companies')
def manage_companies():

    search = request.args.get('search')

    cur = mysql.connection.cursor()

    if search:

        cur.execute("""
            SELECT *
            FROM companies
            WHERE company_name LIKE %s
            OR email LIKE %s
        """, (
            '%' + search + '%',
            '%' + search + '%'
        ))

    else:

        cur.execute("SELECT * FROM companies")

    companies = cur.fetchall()

    cur.close()

    return render_template(
        'manage_companies.html',
        companies=companies
    )

@app.route('/delete_company/<int:id>')
def delete_company(id):

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM companies WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    return redirect('/manage_companies')

@app.route('/delete_student/<int:id>')
def delete_student(id):

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM students WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    return redirect('/manage_students')
@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):

    cur = mysql.connection.cursor()

    cur.execute(
        "UPDATE students SET placement_status=%s WHERE id=%s",
        (status, id)
    )

    mysql.connection.commit()

    cur.close()

    return redirect('/manage_students')

@app.route('/company_applicants')
def company_applicants():

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM applications
        ORDER BY applied_at DESC
    """)

    applications = cur.fetchall()

    cur.close()

    return render_template(
        'company_applicants.html',
        applications=applications
    )
@app.route('/company_dashboard')
def company_dashboard():
    return redirect('/company_login')

if __name__ == '__main__':
    app.run(debug=True)