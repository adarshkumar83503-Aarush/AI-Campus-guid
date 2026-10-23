import os
import random
import time
import datetime
import sqlite3
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "glbajaj_super_secret_session_2026")

DB_FILE = "campus_data.db"
ADMIN_PASSCODE = "VisionX@2026"

# 4 Core Team Admins Allowed to Access
CORE_ADMINS = {
    "25116CN001": {"name": "Adarsh", "email": "adarshkumar83503@gmail.com", "role": "Lead Architect"},
    "25116CN407": {"name": "Akansha", "email": "akanshasingh16806@gmail.com", "role": "Core Admin"},
    "25116CN091": {"name": "Aisha", "email": "pandeyaisha829@gmail.com", "role": "Core Admin"},
    "25116CN029": {"name": "Aditya", "email": "aditya33322@gmail.com", "role": "Core Admin"}
}

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE,
            admission_no TEXT,
            category TEXT,
            location TEXT,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    """)
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

STUDENT_OTP_STORE = {}
VISITOR_OTP_STORE = {}

@app.route("/")
def index():
    return render_template("index.html", locations=CAMPUS_DATA)

# ================= 🔐 TEAM ADMIN CONSOLE =================
@app.route("/admin", methods=["GET", "POST"])
def admin_portal():
    error = None
    if request.method == "POST":
        admin_id = request.form.get("admin_id", "").strip().upper()
        passcode = request.form.get("passcode", "").strip()

        # Sirf 4 members allow honge
        if admin_id in CORE_ADMINS and passcode == ADMIN_PASSCODE:
            session["is_team_admin"] = True
            session["admin_name"] = CORE_ADMINS[admin_id]["name"]
            session["admin_role"] = CORE_ADMINS[admin_id]["role"]
            return redirect(url_for("admin_portal"))
        else:
            error = "Access Denied: Sirf 4 authorized core team members hi login kar sakte hain."

    if not session.get("is_team_admin", False):
        return render_template("admin.html", authenticated=False, error=error)

    # Database se saara data retrieve karein
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Complaints
    cursor.execute("SELECT ticket_id, admission_no, category, location, description, status, created_at FROM complaints ORDER BY id DESC")
    all_complaints = [
        {"ticket_id": r[0], "admission_no": r[1], "category": r[2], "location": r[3], "description": r[4], "status": r[5], "created_at": r[6]}
        for r in cursor.fetchall()
    ]

    # 2. Visitors (Folder Categorization)
    cursor.execute("SELECT pass_id, name, mobile, purpose, entry_time FROM visitors ORDER BY id DESC")
    all_visitors = [
        {"pass_id": r[0], "name": r[1], "mobile": r[2], "purpose": r[3], "entry_time": r[4]}
        for r in cursor.fetchall()
    ]
    conn.close()

    # Separate Lists into Virtual Folders
    admission_visitors = [v for v in all_visitors if "Admission" in v["purpose"]]
    parent_visitors = [v for v in all_visitors if "Parent" in v["purpose"]]
    placement_visitors = [v for v in all_visitors if "Placement" in v["purpose"]]
    fest_visitors = [v for v in all_visitors if "Fest" in v["purpose"] or "Event" in v["purpose"]]
    other_visitors = [v for v in all_visitors if v not in admission_visitors and v not in parent_visitors and v not in placement_visitors and v not in fest_visitors]

    return render_template("admin.html",
                           authenticated=True,
                           admin_name=session.get("admin_name", "Team Member"),
                           admin_role=session.get("admin_role", "Core"),
                           complaints=all_complaints,
                           all_visitors=all_visitors,
                           admission_visitors=admission_visitors,
                           parent_visitors=parent_visitors,
                           placement_visitors=placement_visitors,
                           fest_visitors=fest_visitors,
                           other_visitors=other_visitors,
                           core_team=CORE_ADMINS)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_portal"))

# ================= 🪪 VISITOR AUTH & DATABASE =================
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
        VISITOR_OTP_STORE[mobile] = {"otp": otp, "name": name, "mobile": mobile, "purpose": purpose, "expires": time.time() + 300}
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
            name = rec["name"]
            purpose = rec["purpose"]
            del VISITOR_OTP_STORE[mobile]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO visitors (pass_id, name, mobile, purpose, entry_time) VALUES (?, ?, ?, ?, ?)",
                       (pass_id, name, mobile, purpose, entry_time))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "visitor": {"pass_id": pass_id, "name": name, "entry_time": entry_time}})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ================= 🎓 STUDENT AUTH =================
@app.route("/student/send-otp", methods=["POST"])
def student_send_otp():
    try:
        data = request.get_json(silent=True) or {}
        adm = str(data.get("admission_no", "")).strip().upper()
        if adm not in CORE_ADMINS and adm != "25116CN001":
            return jsonify({"success": False, "message": "ID register nahi hai."}), 404
        otp = str(random.randint(100000, 999999))
        STUDENT_OTP_STORE[adm] = {"otp": otp, "expires": time.time() + 300}
        return jsonify({"success": True, "message": f"OTP: {otp}", "otp": otp})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/student/verify-otp", methods=["POST"])
def student_verify_otp():
    try:
        data = request.get_json(silent=True) or {}
        adm = str(data.get("admission_no", "")).strip().upper()
        session["user_type"] = "student"
        session["user_name"] = CORE_ADMINS.get(adm, {}).get("name", "Student")
        return jsonify({"success": True, "user": {"name": session["user_name"]}})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ================= ⚠️ COMPLAINTS & LOST FOUND API =================
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    try:
        data = request.get_json(silent=True) or {}
        desc = str(data.get("description", "")).strip()
        loc = str(data.get("location", "Campus")).strip()
        cat = str(data.get("category", "General")).strip()
        adm = str(data.get("admission_no", "Guest")).strip()

        tid = f"GLB-{random.randint(1000, 9999)}"
        created_at = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO complaints (ticket_id, admission_no, category, location, description, status, created_at) VALUES (?, ?, ?, ?, ?, 'Pending', ?)",
                       (tid, adm, cat, loc, desc, created_at))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "ticket_id": tid})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/complaints", methods=["GET"])
def api_get_complaints():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT ticket_id, admission_no, category, location, description, status, created_at FROM complaints ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"ticket_id": r[0], "admission_no": r[1], "category": r[2], "location": r[3], "description": r[4], "status": r[5], "created_at": r[6]} for r in rows])

@app.route("/api/lost-found", methods=["GET", "POST"])
def api_lost_found():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        created_at = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
        cursor.execute("INSERT INTO lost_found (type, title, location, contact, created_at) VALUES (?, ?, ?, ?, ?)",
                       (data.get("type", "Lost"), data.get("title", ""), data.get("location", ""), data.get("contact", ""), created_at))
        conn.commit()
        conn.close()
        return jsonify({"success": True})

    cursor.execute("SELECT type, title, location, contact FROM lost_found ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"type": r[0], "title": r[1], "location": r[2], "contact": r[3]} for r in rows])

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=False)
