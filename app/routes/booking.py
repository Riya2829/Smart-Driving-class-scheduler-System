from flask import Blueprint, render_template, session, redirect, url_for
from app import mysql

booking_bp = Blueprint('booking', __name__)

# slot viewing
@booking_bp.route('/view_slots')
def view_slots():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))

    student_id = session['user_id']

    cursor = mysql.connection.cursor()

    # Get student's school
    cursor.execute("SELECT school_id FROM students WHERE id=%s", (student_id,))
    school_id = cursor.fetchone()[0]

    # Get slots of that school
    cursor.execute("""
    SELECT 
        slots.id,
        instructors.name,
        slots.date,
        slots.time,
        slots.capacity,
        COUNT(bookings.id) as booked_count

    FROM slots

    JOIN instructors 
        ON slots.instructor_id = instructors.id

    LEFT JOIN bookings 
        ON slots.id = bookings.slot_id

    WHERE instructors.school_id = %s

    AND TIMESTAMP(slots.date, slots.time) > NOW()

    GROUP BY slots.id

    HAVING booked_count < slots.capacity
""", (school_id,))

    slots = cursor.fetchall()
    cursor.close()

    return render_template('view_slots.html', slots=slots)

# Slot Booking
@booking_bp.route('/book/<int:slot_id>')
def book_slot(slot_id):

    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))

    student_id = session['user_id']

    cursor = mysql.connection.cursor()

    # ✅ Check if student already booked this slot
    cursor.execute("""
        SELECT *
        FROM bookings
        WHERE student_id = %s
        AND slot_id = %s
    """, (student_id, slot_id))

    existing = cursor.fetchone()

    if existing:
        cursor.close()
        return "You already booked this slot ❌"

    # ✅ Get slot capacity
    cursor.execute("""
        SELECT capacity
        FROM slots
        WHERE id = %s
    """, (slot_id,))

    slot = cursor.fetchone()

    if not slot:
        cursor.close()
        return "Slot not found ❌"

    capacity = slot[0]

    # ✅ Count booked students
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE slot_id = %s
    """, (slot_id,))

    booked_count = cursor.fetchone()[0]

    # ❌ Slot full
    if booked_count >= capacity:
        cursor.close()
        return "Slot Full ❌"

    # ✅ Insert booking
    cursor.execute("""
        INSERT INTO bookings (student_id, slot_id)
        VALUES (%s, %s)
    """, (student_id, slot_id))

    mysql.connection.commit()

    cursor.close()

    return redirect(url_for('auth.student_dashboard'))

# Slot cancellation
@booking_bp.route('/cancel/<int:slot_id>')
def cancel_booking(slot_id):
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))

    student_id = session['user_id']
    cursor = mysql.connection.cursor()

    # Delete booking
    cursor.execute(
        "DELETE FROM bookings WHERE student_id=%s AND slot_id=%s",
        (student_id, slot_id)
    )

    # # Make slot available again
    # cursor.execute(
    #     "UPDATE slots SET is_available = TRUE WHERE id=%s",
    #     (slot_id,)
    # )

    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('auth.student_dashboard'))