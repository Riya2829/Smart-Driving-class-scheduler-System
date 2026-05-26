from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))


# ---------------- REGISTER ----------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    cursor = mysql.connection.cursor()

    # 🔹 Fetch schools (IMPORTANT)
    cursor.execute("SELECT id, name FROM schools")
    schools = cursor.fetchall()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        if role == 'admin':
            cursor.execute(
                "INSERT INTO schools (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
        else:
            school_id = request.form['school_id']

            cursor.execute(
                "INSERT INTO students (name, email, password, school_id) VALUES (%s, %s, %s, %s)",
                (name, email, password, school_id)
            )

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('auth.login'))

    cursor.close()
    return render_template('register.html', schools=schools)


# ---------------- LOGIN ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()

        # Check in students
        cursor.execute("SELECT * FROM students WHERE email=%s", (email,))
        student = cursor.fetchone()

        if student and check_password_hash(student[3], password):
            session['user_id'] = student[0]
            session['role'] = 'student'
            return redirect(url_for('auth.student_dashboard'))

        # Check in admins
        cursor.execute("SELECT * FROM schools WHERE email=%s", (email,))
        admin = cursor.fetchone()

        if admin and check_password_hash(admin[3], password):
            session['user_id'] = admin[0]
            session['role'] = 'admin'
            return redirect(url_for('auth.admin_dashboard'))

        return "Invalid Credentials ❌"

    return render_template('login.html')


# ---------------- DASHBOARDS ----------------
@auth_bp.route('/student_dashboard')
def student_dashboard():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))

    student_id = session['user_id']
    cursor = mysql.connection.cursor()

    cursor.execute("""
    SELECT 
        slots.id,
        instructors.name,
        slots.date,
        slots.time
    FROM bookings
    JOIN slots ON bookings.slot_id = slots.id
    JOIN instructors ON slots.instructor_id = instructors.id
    WHERE bookings.student_id = %s
    AND TIMESTAMP(slots.date, slots.time) > NOW()
""", (student_id,))

    bookings = cursor.fetchall()
    cursor.close()

    return render_template('dashboard_student.html', bookings=bookings)


@auth_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    school_id = session['user_id']

    cursor = mysql.connection.cursor()
    
    # Get school name
    cursor.execute(
    "SELECT name FROM schools WHERE id=%s",
    (school_id,)
    )

    school_name = cursor.fetchone()[0]
    
    cursor.execute("""
    SELECT 
        slots.id,
        instructors.name,
        slots.date,
        slots.time,
        students.name
    FROM slots
    JOIN instructors ON slots.instructor_id = instructors.id
    LEFT JOIN bookings ON slots.id = bookings.slot_id
    LEFT JOIN students ON bookings.student_id = students.id
    WHERE instructors.school_id = %s
    AND TIMESTAMP(slots.date, slots.time) > NOW()
""", (school_id,))

    slots = cursor.fetchall()
    cursor.close()

    return render_template(
    'dashboard_admin.html',
    slots=slots,
    school_name=school_name
)

# ---------------- LOGOUT ----------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))