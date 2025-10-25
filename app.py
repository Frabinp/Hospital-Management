# Hospital Management System - Main Application File
# This file contains all Flask routes, database operations, and business logic for the hospital management system

# Import Flask modules for web application functionality
from flask import Flask, render_template, request, redirect, url_for, flash, session
# Import sqlite3 for database operations and SQL queries
import sqlite3
# Import password hashing functions for secure user authentication
from werkzeug.security import generate_password_hash, check_password_hash
# Import functools for creating decorators (login_required, admin_required)
from functools import wraps
# Import datetime for timestamp operations and date handling
from datetime import datetime

# Create Flask application instance with the name of the current module
app = Flask(__name__)
# Set secret key for session management, CSRF protection, and secure cookies
# In production, this should be a secure random string
app.secret_key = 'your-secret-key-change-this-in-production'
# Define the SQLite database filename
DB_NAME = "database.db"

# Initialize database function - creates all required tables and default data
def init_db():
    # Connect to SQLite database (creates database file if it doesn't exist)
    conn = sqlite3.connect(DB_NAME)
    # Create cursor object to execute SQL commands
    cursor = conn.cursor()
    
    # Create patients table to store patient information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing primary key for unique patient ID
            name TEXT,                             -- Patient's full name
            age INTEGER,                           -- Patient's age in years
            gender TEXT,                           -- Patient's gender (Male/Female/Other)
            address TEXT,                          -- Patient's home address
            phone TEXT                             -- Patient's contact phone number
        )
    """)
    
    # Create appointments table to store appointment scheduling information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing primary key for unique appointment ID
            patient_name TEXT,                     -- Name of the patient for the appointment
            doctor_name TEXT,                      -- Name of the doctor for the appointment
            date TEXT,                             -- Date of the appointment (YYYY-MM-DD format)
            time TEXT                              -- Time of the appointment (HH:MM format)
        )
    """)
    
    # Create users table for authentication and user management system
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing primary key for unique user ID
            username TEXT UNIQUE NOT NULL,         -- Unique username for login (cannot be duplicated)
            password_hash TEXT NOT NULL,           -- Hashed password for security (never store plain text)
            role TEXT NOT NULL,                    -- User role: admin, doctor, or receptionist
            full_name TEXT,                        -- User's full name for display purposes
            email TEXT,                            -- User's email address for contact
            created_at TEXT DEFAULT CURRENT_TIMESTAMP  -- Timestamp when user account was created
        )
    """)
    
    # Create medical records table to store patient medical history and treatment information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing primary key for unique record ID
            patient_id INTEGER,                    -- Foreign key linking to patients table
            doctor_name TEXT,                      -- Name of the doctor who treated the patient
            diagnosis TEXT,                        -- Medical diagnosis or condition identified
            treatment TEXT,                        -- Treatment provided to the patient
            prescription TEXT,                     -- Prescription details and medications
            notes TEXT,                           -- Additional medical notes and observations
            visit_date TEXT,                      -- Date when the medical visit occurred
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when record was created in system
            FOREIGN KEY (patient_id) REFERENCES patients(id)  -- Foreign key constraint ensuring data integrity
        )
    """)
    
    # Check if any users exist in the database to determine if we need to create default admin
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]  # Get the count of existing users
    
    # Create default admin user if no users exist (first time setup)
    if user_count == 0:
        # Hash the default admin password for security
        admin_password = generate_password_hash('admin123')
        # Insert default admin user into the database
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        """, ('admin', admin_password, 'admin', 'System Administrator', 'admin@hospital.com'))
    
    # Commit all database changes to make them permanent
    conn.commit()
    # Close the database connection to free up resources
    conn.close()

# Call the database initialization function when the application starts
init_db()

# Authentication decorator - ensures user is logged in before accessing protected routes
def login_required(f):
    @wraps(f)  # Preserve the original function's metadata (name, docstring, etc.)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in by verifying session contains user_id
        if 'user_id' not in session:
            # Display error message to user
            flash('Please log in to access this page.', 'error')
            # Redirect to login page
            return redirect(url_for('login'))
        # If user is logged in, execute the original function
        return f(*args, **kwargs)
    return decorated_function

# Admin-only decorator - ensures only admin users can access admin functions
def admin_required(f):
    @wraps(f)  # Preserve the original function's metadata (name, docstring, etc.)
    def decorated_function(*args, **kwargs):
        # First check if user is logged in
        if 'user_id' not in session:
            # Display error message to user
            flash('Please log in to access this page.', 'error')
            # Redirect to login page
            return redirect(url_for('login'))
        # Check if user has admin role
        if session.get('user_role') != 'admin':
            # Display error message for insufficient permissions
            flash('Admin access required.', 'error')
            # Redirect to dashboard (not login, since user is already logged in)
            return redirect(url_for('dashboard'))
        # If user is admin, execute the original function
        return f(*args, **kwargs)
    return decorated_function

# Login route - handles user authentication (both GET and POST methods)
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle POST request when user submits login form
    if request.method == 'POST':
        # Get username and password from the submitted form
        username = request.form['username']
        password = request.form['password']
        
        # Connect to database to verify user credentials
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Query database for user with matching username
        cursor.execute("SELECT id, username, password_hash, role, full_name FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()  # Get the first matching user record
        conn.close()  # Close database connection
        
        # Check if user exists and password is correct using secure password verification
        if user and check_password_hash(user[2], password):
            # Set session variables for the logged-in user
            session['user_id'] = user[0]        # Store user ID in session
            session['username'] = user[1]       # Store username in session
            session['user_role'] = user[3]      # Store user role in session
            session['full_name'] = user[4]      # Store full name in session
            # Display success message to user
            flash('Login successful!', 'success')
            # Redirect to dashboard after successful login
            return redirect(url_for('dashboard'))
        else:
            # Display error message for invalid credentials
            flash('Invalid username or password.', 'error')
    
    # Render login template for GET request (initial page load)
    return render_template('login.html')

# Logout route - clears user session and logs out the user
@app.route('/logout')
def logout():
    # Clear all session data to log out the user
    session.clear()
    # Display logout confirmation message
    flash('You have been logged out.', 'info')
    # Redirect to login page after logout
    return redirect(url_for('login'))

# Dashboard route - main page after successful login, shows system statistics
@app.route('/dashboard')
@login_required  # Require user to be logged in to access dashboard
def dashboard():
    # Connect to database to fetch statistics
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get total number of patients in the system
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]  # Get the count from the first column
    
    # Get total number of appointments in the system
    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cursor.fetchone()[0]  # Get the count from the first column
    
    # Get recent appointments (last 5 appointments ordered by date and time)
    cursor.execute("SELECT * FROM appointments ORDER BY date DESC, time DESC LIMIT 5")
    recent_appointments = cursor.fetchall()  # Get all matching records
    
    # Close database connection to free up resources
    conn.close()
    
    # Prepare statistics dictionary to pass to the dashboard template
    stats = {
        'total_patients': total_patients,           # Total number of patients
        'total_appointments': total_appointments,   # Total number of appointments
        'total_doctors': 3,                        # Hardcoded number of doctors (as per plan)
        'recent_appointments': recent_appointments  # Recent appointments for display
    }
    
    # Render dashboard template with statistics data
    return render_template('dashboard.html', stats=stats)

# Home route - redirects to dashboard if logged in, otherwise shows public homepage
@app.route('/')
def index():
    # Check if user is already logged in by verifying session contains user_id
    if 'user_id' in session:
        # If logged in, redirect to dashboard
        return redirect(url_for('dashboard'))
    # If not logged in, show public homepage
    return render_template("index.html")

# User Management Routes (Admin Only) - These routes are only accessible by admin users

# View all users route - displays list of all system users
@app.route('/users')
@admin_required  # Require admin role to access user management
def view_users():
    # Connect to database to fetch user information
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Query all users ordered by creation date (newest first)
    cursor.execute("SELECT id, username, role, full_name, email, created_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()  # Get all user records
    conn.close()  # Close database connection
    # Render users template with user data
    return render_template('users.html', users=users)

# Add new user route - allows admin to create new user accounts
@app.route('/add_user', methods=['GET', 'POST'])
@admin_required  # Require admin role to add users
def add_user():
    # Handle POST request when user submits the add user form
    if request.method == 'POST':
        # Get form data from the submitted form
        username = request.form['username']        # Get username from form
        password = request.form['password']       # Get password from form
        role = request.form['role']               # Get user role from form
        full_name = request.form['full_name']     # Get full name from form
        email = request.form['email']             # Get email from form
        
        try:
            # Connect to database to insert new user
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            # Hash the password for security before storing
            password_hash = generate_password_hash(password)
            # Insert new user into the database
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, role, full_name, email))
            # Commit the database transaction
            conn.commit()
            conn.close()  # Close database connection
            # Display success message to user
            flash('User created successfully!', 'success')
            # Redirect to users list page
            return redirect(url_for('view_users'))
        except sqlite3.IntegrityError:
            # Handle case where username already exists (unique constraint violation)
            flash('Username already exists!', 'error')
        except Exception as e:
            # Handle any other database or system errors
            flash('Error creating user: ' + str(e), 'error')
    
    # Render add user form template for GET request (initial page load)
    return render_template('add_user.html')

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form.get('password')
        
        try:
            if password:
                password_hash = generate_password_hash(password)
                cursor.execute("""
                    UPDATE users SET username=?, password_hash=?, role=?, full_name=?, email=?
                    WHERE id=?
                """, (username, password_hash, role, full_name, email, id))
            else:
                cursor.execute("""
                    UPDATE users SET username=?, role=?, full_name=?, email=?
                    WHERE id=?
                """, (username, role, full_name, email, id))
            
            conn.commit()
            conn.close()
            flash('User updated successfully!', 'success')
            return redirect(url_for('view_users'))
        except Exception as e:
            flash('Error updating user: ' + str(e), 'error')
    
    cursor.execute("SELECT id, username, role, full_name, email FROM users WHERE id=?", (id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('view_users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:id>')
@admin_required
def delete_user(id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (id,))
        conn.commit()
        conn.close()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting user: ' + str(e), 'error')
    
    return redirect(url_for('view_users'))

# Medical Records Routes
@app.route('/medical_records')
@login_required
def view_medical_records():
    search = request.args.get('search', '')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if search:
        cursor.execute("""
            SELECT mr.*, p.name as patient_name 
            FROM medical_records mr 
            JOIN patients p ON mr.patient_id = p.id 
            WHERE p.name LIKE ? OR mr.doctor_name LIKE ? OR mr.diagnosis LIKE ?
            ORDER BY mr.visit_date DESC
        """, (f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("""
            SELECT mr.*, p.name as patient_name 
            FROM medical_records mr 
            JOIN patients p ON mr.patient_id = p.id 
            ORDER BY mr.visit_date DESC
        """)
    
    records = cursor.fetchall()
    conn.close()
    return render_template('medical_records.html', records=records, search=search)

@app.route('/add_medical_record', methods=['GET', 'POST'])
@login_required
def add_medical_record():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_name = request.form['doctor_name']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        prescription = request.form['prescription']
        notes = request.form['notes']
        visit_date = request.form['visit_date']
        
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO medical_records (patient_id, doctor_name, diagnosis, treatment, prescription, notes, visit_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (patient_id, doctor_name, diagnosis, treatment, prescription, notes, visit_date))
            conn.commit()
            conn.close()
            flash('Medical record added successfully!', 'success')
            return redirect(url_for('view_medical_records'))
        except Exception as e:
            flash('Error adding medical record: ' + str(e), 'error')
    
    # Get patients for dropdown
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM patients ORDER BY name")
    patients = cursor.fetchall()
    conn.close()
    
    return render_template('add_medical_record.html', patients=patients)

@app.route('/view_medical_record/<int:id>')
@login_required
def view_medical_record(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mr.*, p.name as patient_name 
        FROM medical_records mr 
        JOIN patients p ON mr.patient_id = p.id 
        WHERE mr.id=?
    """, (id,))
    record = cursor.fetchone()
    conn.close()
    
    if not record:
        flash('Medical record not found!', 'error')
        return redirect(url_for('view_medical_records'))
    
    return render_template('view_medical_record.html', record=record)

@app.route('/edit_medical_record/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_medical_record(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_name = request.form['doctor_name']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        prescription = request.form['prescription']
        notes = request.form['notes']
        visit_date = request.form['visit_date']
        
        try:
            cursor.execute("""
                UPDATE medical_records 
                SET patient_id=?, doctor_name=?, diagnosis=?, treatment=?, prescription=?, notes=?, visit_date=?
                WHERE id=?
            """, (patient_id, doctor_name, diagnosis, treatment, prescription, notes, visit_date, id))
            conn.commit()
            conn.close()
            flash('Medical record updated successfully!', 'success')
            return redirect(url_for('view_medical_records'))
        except Exception as e:
            flash('Error updating medical record: ' + str(e), 'error')
    
    cursor.execute("SELECT * FROM medical_records WHERE id=?", (id,))
    record = cursor.fetchone()
    
    # Get patients for dropdown
    cursor.execute("SELECT id, name FROM patients ORDER BY name")
    patients = cursor.fetchall()
    conn.close()
    
    if not record:
        flash('Medical record not found!', 'error')
        return redirect(url_for('view_medical_records'))
    
    return render_template('edit_medical_record.html', record=record, patients=patients)

@app.route('/delete_medical_record/<int:id>')
@login_required
def delete_medical_record(id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medical_records WHERE id=?", (id,))
        conn.commit()
        conn.close()
        flash('Medical record deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting medical record: ' + str(e), 'error')
    
    return redirect(url_for('view_medical_records'))

@app.route('/patient_history/<int:patient_id>')
@login_required
def patient_history(patient_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get patient info
    cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
    patient = cursor.fetchone()
    
    # Get medical records
    cursor.execute("""
        SELECT * FROM medical_records 
        WHERE patient_id=? 
        ORDER BY visit_date DESC
    """, (patient_id,))
    records = cursor.fetchall()
    conn.close()
    
    if not patient:
        flash('Patient not found!', 'error')
        return redirect(url_for('view_patients'))
    
    return render_template('patient_history.html', patient=patient, records=records)

# Register patient (from homepage form)
@app.route('/register_patient', methods=['POST'])
@login_required
def register_patient():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    address = request.form['address']
    phone = request.form['phone']

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patients (name, age, gender, address, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (name, age, gender, address, phone))
        conn.commit()
        conn.close()
        flash('Patient registered successfully!', 'success')
        return redirect(url_for('view_patients'))
    except Exception as e:
        flash('Error registering patient: ' + str(e), 'error')
        return redirect(url_for('index'))

# Book appointment (from homepage form)
@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    patient_name = request.form['patient_name']
    doctor_name = request.form['doctor_name']
    date = request.form['date']
    time = request.form['time']

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO appointments (patient_name, doctor_name, date, time)
            VALUES (?, ?, ?, ?)
        """, (patient_name, doctor_name, date, time))
        conn.commit()
        conn.close()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('view_appointments'))
    except Exception as e:
        flash('Error booking appointment: ' + str(e), 'error')
        return redirect(url_for('index'))

# View patients
@app.route('/view_patients')
@login_required
def view_patients():
    search = request.args.get('search', '')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if search:
        cursor.execute("SELECT * FROM patients WHERE name LIKE ? OR phone LIKE ? ORDER BY name", (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("SELECT * FROM patients ORDER BY name")
    
    patients = cursor.fetchall()
    conn.close()
    return render_template("view_patients.html", patients=patients, search=search)

# Update patient
@app.route('/update_patient/<int:id>', methods=['GET', 'POST'])
@login_required
def update_patient(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        address = request.form['address']
        phone = request.form['phone']
        try:
            cursor.execute("""
                UPDATE patients
                SET name=?, age=?, gender=?, address=?, phone=?
                WHERE id=?
            """, (name, age, gender, address, phone, id))
            conn.commit()
            conn.close()
            flash('Patient updated successfully!', 'success')
            return redirect(url_for('view_patients'))
        except Exception as e:
            flash('Error updating patient: ' + str(e), 'error')
            return redirect(url_for('view_patients'))
    cursor.execute("SELECT * FROM patients WHERE id=?", (id,))
    patient = cursor.fetchone()
    conn.close()
    return render_template("update_patient.html", patient=patient)

# Delete patient
@app.route('/delete_patient/<int:id>')
@login_required
def delete_patient(id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id=?", (id,))
        conn.commit()
        conn.close()
        flash('Patient deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting patient: ' + str(e), 'error')
    return redirect(url_for('view_patients'))

# View appointments
@app.route('/view_appointments')
@login_required
def view_appointments():
    search = request.args.get('search', '')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if search:
        cursor.execute("SELECT * FROM appointments WHERE patient_name LIKE ? OR doctor_name LIKE ? ORDER BY date DESC, time DESC", (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("SELECT * FROM appointments ORDER BY date DESC, time DESC")
    
    appointments = cursor.fetchall()
    conn.close()
    return render_template("view_appointments.html", appointments=appointments, search=search)

# Update appointment
@app.route('/update_appointment/<int:id>', methods=['GET', 'POST'])
@login_required
def update_appointment(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        doctor_name = request.form['doctor_name']
        date = request.form['date']
        time = request.form['time']
        try:
            cursor.execute("""
                UPDATE appointments
                SET patient_name=?, doctor_name=?, date=?, time=?
                WHERE id=?
            """, (patient_name, doctor_name, date, time, id))
            conn.commit()
            conn.close()
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('view_appointments'))
        except Exception as e:
            flash('Error updating appointment: ' + str(e), 'error')
            return redirect(url_for('view_appointments'))
    cursor.execute("SELECT * FROM appointments WHERE id=?", (id,))
    appointment = cursor.fetchone()
    conn.close()
    return render_template("update_appointment.html", appointment=appointment)

# Delete appointment
@app.route('/delete_appointment/<int:id>')
@login_required
def delete_appointment(id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id=?", (id,))
        conn.commit()
        conn.close()
        flash('Appointment deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting appointment: ' + str(e), 'error')
    return redirect(url_for('view_appointments'))

if __name__ == "__main__":
    app.run(debug=True)
