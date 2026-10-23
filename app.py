import os
import random
import time
import datetime
import sqlite3
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "glbajaj_super_secret_session_2026")

DB_FILE = "campus_data.db"
ADMIN_PASSCODE = "GLB@ADMIN2026"
SENDER_EMAIL = "adarshkumar83503@gmail.com"
SENDER_APP_PASSWORD = "sfrl khsi gaso roni"

# ================= 🗄️ SQLITE DATABASE INITIALIZATION =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # 1. Permanent Visitors Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pass_id TEXT UNIQUE,
            name TEXT,
            mobile TEXT,
            purpose TEXT,
            entry_time TEXT
        )
    """)
    # 2. Permanent Complaints Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE,
            admission_no TEXT,
            category TEXT,
            location TEXT,
            description TEXT,
            created_at TEXT
        )
    """)
    # 3. Permanent Lost & Found Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lost_found (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            title TEXT,
            location TEXT,
            contact TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

CAMPUS_DATA = {
    "ab1": {"name": "Academic Block 1 (AB-1)", "lat": 28.4725, "lng": 77.4891, "desc": "First Year Classes & Dean Office"},
    "ab2": {"name": "Academic Block 2 (AB-2)", "lat": 28.4728, "lng": 77.4896, "desc": "CSE, IT & AI Labs"},
    "library": {"name": "Central Knowledge Park Library", "lat": 28.4730, "lng": 77.4894, "desc": "Reading Halls & Digital Library"},
    "audi": {"name": "Mahatma Gandhi Central Auditorium", "lat": 28.4735, "lng": 77.4889, "desc": "Auditorium & Events"},
    "cafeteria": {"name": "Student Cafeteria & Food Court", "lat": 28.4721, "lng": 77.4890, "desc": "Dining Courtyard"}
}

STUDENTS_DB = {
    "25116CN001": {"name": "Adarsh", "email": "adarshkumar83503@gmail.com"},
    "25116CN407": {"name": "Akansha", "email": "akanshasingh16806@gmail.com"},
    "25116CN091": {"name": "Aisha", "email": "pandeyaisha829@gmail.com"},
    "25116CN029": {"name": "Aditya", "email": "aditya33322@gmail.com"}
}

STUDENT_OTP_STORE = {}
VISITOR_OTP_STORE = {}

@app.route("/")
def index():
    return render_template("index.html", locations=CAMPUS_DATA)

# ================= 🎓 STUDENT AUTH =================
@app.route("/student/send-otp", methods=["POST"])
def student_send_otp():
    try:
        data = request.get_json(silent=True) or {}
        adm = str(data.get("admission_no", "")).strip().upper()

        if not adm:
            return jsonify({"success": False, "message": "Admission ID enter karein."}), 400

        if adm not in STUDENTS_DB:
            return jsonify({"success": False, "message": f"Admission ID '{adm}' nahi mili! (Demo: 25116CN001)"}), 404

        student = STUDENTS_DB[adm]
        recipient_email = student["email"]
        otp = str(random.randint(100000, 999999))
        STUDENT_OTP_STORE[adm] = {"otp": otp, "expires": time.time() + 300}

        email_sent = False
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = "GL Bajaj Campus Guide - OTP"
            body = f"Namaste {student['name']},\n\nAapka login OTP hai: {otp}\nYeh agle 5 minute tak valid hai."
            msg.attach(MIMEText(body, 'plain'))

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=3) as server:
                server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
                server.send_message(msg)
            email_sent = True
        except Exception as mail_err:
            print(f"[SMTP Warning] {mail_err}", flush=True)

        return jsonify({
            "success": True,
            "message": f"OTP email par bhej diya gaya hai!" if email_sent else f"OTP: {otp} (Demo Mode)",
            "otp": otp,
            "student_name": student["name"]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/student/verify-otp", methods=["POST"])
def student_verify_otp():
    try:
        data = request.get_json(silent=True) or {}
        adm = str(data.get("admission_no", "")).strip().upper()
        user_otp = str(data.get("otp", "")).strip()

        if adm not in STUDENT_OTP_STORE:
            return jsonify({"success": False, "message": "Pehle OTP generate karein."}), 400

        if user_otp == STUDENT_OTP_STORE[adm]["otp"]:
            del STUDENT_OTP_STORE[adm]
            session["user_type"] = "student"
            session["user_name"] = STUDENTS_DB[adm]["name"]
            return jsonify({"success": True, "user": STUDENTS_DB[adm]})

        return jsonify({"success": False, "message": "Galat OTP! Kripya sahi OTP daalein."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ================= 🪪 VISITOR AUTH & DATABASE INSERT =================
@app.route("/visitor/send-otp", methods=["POST"])
def visitor_send_otp():
    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        mobile = str(data.get("mobile", "")).strip()
        aadhaar = str(data.get("aadhaar", "")).strip()
        purpose = str(data.get("purpose", "")).strip()

        if not name or not mobile or not aadhaar:
            return jsonify({"success": False, "message": "Sabhi details bharna zaroori hai."}), 400

        otp = str(random.randint(100000, 999999))
        VISITOR_OTP_STORE[mobile] = {
            "otp": otp,
            "name": name,
            "mobile": mobile,
            "purpose": purpose,
            "expires": time.time() + 300
        }

        print(f"[VISITOR OTP] {name} ({mobile}) -> {otp}", flush=True)
        return jsonify({"success": True, "message": f"Verification OTP: {otp}", "otp": otp})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/visitor/verify-otp", methods=["POST"])
def visitor_verify_otp():
    try:
        data = request.get_json(silent=True) or {}
        mobile = str(data.get("mobile", "")).strip()
        user_otp = str(data.get("otp", "")).strip()

        pass_id = f"GP-{random.randint(1000, 9999)}"
        entry_time = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
        name = "Campus Visitor"
        purpose = "General Visit"

        if mobile in VISITOR_OTP_STORE:
            rec = VISITOR_OTP_STORE[mobile]
            if user_otp == rec["otp"]:
                name = rec["name"]
                purpose = rec["purpose"]
                del VISITOR_OTP_STORE[mobile]

        # SQLite Database me Permanent Insert
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO visitors (pass_id, name, mobile, purpose, entry_time)
            VALUES (?, ?, ?, ?, ?)
        """, (pass_id, name, mobile, purpose, entry_time))
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Gate Pass Registered Permanently!",
            "visitor": {"pass_id": pass_id, "name": name, "entry_time": entry_time}
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ================= 🔍 LOST & FOUND (PERMANENT DB API) =================
@app.route("/api/lost-found", methods=["GET", "POST"])
def api_lost_found():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        created_at = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
        cursor.execute("""
            INSERT INTO lost_found (type, title, location, contact, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (data.get("type", "Lost"), data.get("title", ""), data.get("location", ""), data.get("contact", ""), created_at))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Item registered successfully!"})

    cursor.execute("SELECT type, title, location, contact FROM lost_found ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    items = [{"type": r[0], "title": r[1], "location": r[2], "contact": r[3]} for r in rows]
    return jsonify(items)

# ================= ⚠️ GRIEVANCES & COMPLAINTS =================
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    try:
        data = request.get_json(silent=True) or {}
        desc = str(data.get("description", "")).strip()
        loc = str(data.get("location", "Campus")).strip()
        cat = str(data.get("category", "General")).strip()
        adm = str(data.get("admission_no", "Guest")).strip()

        if not desc:
            return jsonify({"success": False, "message": "Vivaran likhna zaroori hai."}), 400

        tid = f"GLB-{random.randint(1000, 9999)}"
        created_at = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO complaints (ticket_id, admission_no, category, location, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tid, adm, cat, loc, desc, created_at))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Grievance Darj Ho Gayi!", "ticket_id": tid})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ================= 🔐 ADMIN CONSOLE =================
@app.route("/admin", methods=["GET", "POST"])
def admin_portal():
    if request.method == "POST":
        entered = request.form.get("passcode", "").strip()
        if entered == ADMIN_PASSCODE:
            session["is_team_admin"] = True
        else:
            return render_template("admin.html", authenticated=False, error="Galat Passcode! Access Denied.")

    if not session.get("is_team_admin", False):
        return render_template("admin.html", authenticated=False)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT pass_id, name, mobile, purpose, entry_time FROM visitors ORDER BY id DESC")
    all_visitors = [{"pass_id": r[0], "name": r[1], "mobile": r[2], "purpose": r[3], "entry_time": r[4]} for r in cursor.fetchall()]

    cursor.execute("SELECT ticket_id, admission_no, category, location, description, created_at FROM complaints ORDER BY id DESC")
    all_complaints = [{"ticket_id": r[0], "admission_no": r[1], "category": r[2], "location": r[3], "description": r[4], "created_at": r[5]} for r in cursor.fetchall()]
    conn.close()

    return render_template("admin.html",
                           authenticated=True,
                           visitors=all_visitors,
                           complaints=all_complaints,
                           total_visitors=len(all_visitors),
                           total_complaints=len(all_complaints))

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_team_admin", None)
    return render_template("admin.html", authenticated=False, error="Logged out.")

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=False)
