from flask import Blueprint, render_template, session, redirect, url_for
from app import mysql

student_bp = Blueprint('student', __name__)

@student_bp.route('/student_dashboard')
def student_dashboard():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))

    student_id = session['user_id']
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT slots.id, instructors.name, slots.date, slots.time
        FROM bookings
        JOIN slots ON bookings.slot_id = slots.id
        JOIN instructors ON slots.instructor_id = instructors.id
        WHERE bookings.student_id = %s
    """, (student_id,))

    bookings = cursor.fetchall()
    cursor.close()

    return render_template('dashboard_student.html', bookings=bookings)