from flask import Blueprint, render_template, request, session, redirect, url_for
from app import mysql

admin_bp = Blueprint('admin', __name__)

# Slot Creation
@admin_bp.route('/create_slot', methods=['GET', 'POST'])
def create_slot():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        instructor_name = request.form['instructor']
        date = request.form['date']
        time = request.form['time']
        capacity = request.form['capacity']
        school_id = session['user_id']

        cursor = mysql.connection.cursor()

        # Insert instructor
        cursor.execute(
            "INSERT INTO instructors (name, school_id) VALUES (%s, %s)",
            (instructor_name, school_id)
        )
        instructor_id = cursor.lastrowid

        # Insert slot
        cursor.execute(
            "INSERT INTO slots (instructor_id, date, time,capacity) VALUES (%s, %s, %s,%s)",
            (instructor_id, date, time,capacity)
        )

        mysql.connection.commit()
        cursor.close()

        print("Slot inserted successfully")

        return redirect(url_for('auth.admin_dashboard'))

    return render_template('create_slot.html')

@admin_bp.route('/view_students')
def view_students():

    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    school_id = session['user_id']

    cursor = mysql.connection.cursor()

    # Get students of this school only
    cursor.execute("""
        SELECT name, email
        FROM students
        WHERE school_id = %s
    """, (school_id,))

    students = cursor.fetchall()

    cursor.close()

    return render_template(
        'view_students.html',
        students=students
    )