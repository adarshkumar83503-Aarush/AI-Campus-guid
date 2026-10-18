import os
import random
import time
import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = "glbajaj_secure_campus_session_key_2026"

# ==========================================
# 🔐 ADMIN PASSCODE (Only for Team Members)
# ==========================================
ADMIN_PASSCODE = "GLB@ADMIN2026"

# ==========================================
# 📧 EMAIL SMTP CONFIGURATION
# ==========================================
SENDER_EMAIL = "adarshkumar83503@gmail.com"
SENDER_APP_PASSWORD = "sfrl khsi gaso roni"

# ==========================================
# 📍 CAMPUS LOCATIONS
# ==========================================
CAMPUS_DATA = {
    "ab1": {
        "name": "Academic Block 1 (AB-1)",
        "lat": 28.4725,
        "lng": 77.4891,
        "desc": "First Year Classes & Dean Office"
    },
    "ab2": {
        "name": "Academic Block 2 (AB-2)",
        "lat": 28.4728,
        "lng": 77.4896,
        "desc": "CSE, IT & AI Labs"
    },
    "library": {
        "name": "Central Knowledge Park Library",
        "lat": 28.4730,
        "lng": 77.4894,
        "desc": "Reading Halls & Digital Library"
    },
    "audi": {
        "name": "Mahatma Gandhi Central Auditorium",
        "lat": 28.4735,
        "lng": 77.4889,
        "desc": "Auditorium & Events"
    },
    "cafeteria": {
        "name": "Student Cafeteria & Food Court",
        "lat": 28.4721,
        "lng": 77.4890,
        "desc": "Cafeteria & Open Dining Area"
    }
}

# ==========================================
# 👥 IN-MEMORY DATABASES
# ==========================================
STUDENTS_DB = {
    "25116CN001": {"name": "Adarsh", "email": "adarshkumar83503@gmail.com"},
    "25116CN407": {"name": "Akansha", "email": "akanshasingh16806@gmail.com"},
    "25116CN091": {"name": "Aisha", "email": "pandeyaisha829@gmail.com"},
    "25116CN029": {"name": "Aditya", "email": "aditya33322@gmail.com"}
}

STUDENT_OTP_STORE = {}
VISITOR_OTP_STORE = {}
COMPLAINTS_DB = []
VISITORS_DB = []

# ==========================================
# 🌐 ROUTES
# ==========================================
@app.route("/")
def index():
    return render_template("index.html", locations=CAMPUS_DATA)

# ------------------------------------------
# 🎓 1. STUDENT AUTH (Admission No -> Email OTP)
# ------------------------------------------
@app.route("/student/send-otp", methods=["POST"])
def student_send_otp():
    data = request.json or {}
    adm = data.get("admission_no", "").strip().upper()

    if adm not in STUDENTS_DB:
        return jsonify({"success": False, "message": "Admission ID nahi mili! (Demo ID: 25116CN001)"}), 404

    student = STUDENTS_DB[adm]
    recipient_email = student["email"]
    otp = str(random.randint(100000, 999999))
    STUDENT_OTP_STORE[adm] = {"otp": otp, "expires": time.time() + 300}

    print(f"\n[STUDENT OTP] {adm} ({recipient_email}) -> {otp}\n", flush=True)

    email_sent = False
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = "GL Bajaj Campus Guide - Login Verification OTP"

        body = f"""Namaste {student['name']},

Aapka GL Bajaj Student Portal login OTP hai: {otp}

Yeh OTP 5 minute ke liye valid hai. Kripya ise kisi ke sath share na karein.

Best regards,
GL Bajaj Campus Guide Team"""
        msg.attach(MIMEText(body, 'plain'))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=8) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(msg)
        email_sent = True
    except Exception as e:
        print(f"[SMTP Notice] Direct connection delayed or port blocked: {e}", flush=True)

    return jsonify({
        "success": True,
        "email_sent": email_sent,
        "message": f"OTP successfully sent to {recipient_email}!" if email_sent else f"Verification OTP: {otp}",
        "otp": otp,
        "student_name": student["name"]
    })

@app.route("/student/verify-otp", methods=["POST"])
def student_verify_otp():
    data = request.json or {}
    adm = data.get("admission_no", "").strip().upper()
    user_otp = data.get("otp", "").strip()

    if adm not in STUDENT_OTP_STORE:
        return jsonify({"success": False, "message": "Pehle OTP generate karein."}), 400

    if time.time() > STUDENT_OTP_STORE[adm]["expires"]:
        del STUDENT_OTP_STORE[adm]
        return jsonify({"success": False, "message": "OTP expire ho chuka hai."}), 400

    if user_otp == STUDENT_OTP_STORE[adm]["otp"]:
        del STUDENT_OTP_STORE[adm]
        session["user_type"] = "student"
        session["user_name"] = STUDENTS_DB[adm]["name"]
        return jsonify({"success": True, "user": STUDENTS_DB[adm]})

    return jsonify({"success": False, "message": "Galat OTP! Dobara check karein."}), 400

# ------------------------------------------
# 🪪 2. VISITOR GATE PASS & AUTO-LOGGING
# ------------------------------------------
@app.route("/visitor/send-otp", methods=["POST"])
def visitor_send_otp():
    data = request.json or {}
    name = data.get("name", "").strip()
    mobile = data.get("mobile", "").strip()
    aadhaar = data.get("aadhaar", "").strip()
    purpose = data.get("purpose", "").strip()

    if not name or not mobile or not aadhaar or not purpose:
        return jsonify({"success": False, "message": "Saare fields (Naam, Mobile, Aadhaar, Purpose) bharein."}), 400

    if len(mobile) < 10:
        return jsonify({"success": False, "message": "10-digit mobile number daalein."}), 400

    otp = str(random.randint(100000, 999999))
    VISITOR_OTP_STORE[mobile] = {
        "otp": otp,
        "name": name,
        "mobile": mobile,
        "masked_aadhaar": "[Aadhaar Redacted]",
        "purpose": purpose,
        "expires": time.time() + 300
    }

    print(f"\n[VISITOR OTP] Mobile: {mobile} | Name: {name} | OTP: {otp}\n", flush=True)

    return jsonify({
        "success": True,
        "message": f"Mobile Verification OTP: {otp}",
        "otp": otp
    })

@app.route("/visitor/verify-otp", methods=["POST"])
def visitor_verify_otp():
    data = request.json or {}
    mobile = data.get("mobile", "").strip()
    user_otp = data.get("otp", "").strip()

    if mobile not in VISITOR_OTP_STORE:
        return jsonify({"success": False, "message": "OTP session expire ho gaya hai."}), 400

    record = VISITOR_OTP_STORE[mobile]

    if user_otp == record["otp"]:
        pass_id = f"GP-{random.randint(1000, 9999)}"
        entry_time = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

        visitor_entry = {
            "pass_id": pass_id,
            "name": record["name"],
            "mobile": record["mobile"],
            "masked_aadhaar": record["masked_aadhaar"],
            "purpose": record["purpose"],
            "entry_time": entry_time,
            "status": "Checked In"
        }

        # Data automatically stored in central visitors log
        VISITORS_DB.append(visitor_entry)
        del VISITOR_OTP_STORE[mobile]

        return jsonify({
            "success": True,
            "message": "Gate Pass safaltapoorvak generate hua!",
            "visitor": visitor_entry
        })

    return jsonify({"success": False, "message": "Galat OTP!"}), 400

# ------------------------------------------
# ⚠️ 3. COMPLAINTS & GRIEVANCE
# ------------------------------------------
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    data = request.json or {}
    desc = data.get("description", "").strip()
    if not desc:
        return jsonify({"success": False, "message": "Vivaran likhna anivarya hai."}), 400

    tid = f"GLB-{random.randint(1000, 9999)}"
    record = {
        "ticket_id": tid,
        "admission_no": data.get("admission_no", "Guest / Visitor"),
        "category": data.get("category", "General"),
        "location": data.get("location", "Campus"),
        "description": desc,
        "status": "Pending",
        "created_at": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    }
    COMPLAINTS_DB.append(record)
    return jsonify({"success": True, "message": "Complaint darj ho gayi!", "ticket_id": tid})

# ------------------------------------------
# 🔐 4. PROTECTED ADMIN PORTAL (Team Members Only)
# ------------------------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin_portal():
    if request.method == "POST":
        entered = request.form.get("passcode", "").strip()
        if entered == ADMIN_PASSCODE:
            session["is_team_admin"] = True
        else:
            return render_template("admin.html", authenticated=False, error="Galat Team Passcode! Access Denied.")

    is_auth = session.get("is_team_admin", False)
    return render_template("admin.html",
                           authenticated=is_auth,
                           complaints=list(reversed(COMPLAINTS_DB)),
                           visitors=list(reversed(VISITORS_DB)))

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_team_admin", None)
    return render_template("admin.html", authenticated=False, error="Logged out successfully.")

@app.route("/api/complaints/update-status", methods=["POST"])
def update_complaint_status():
    if not session.get("is_team_admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.json or {}
    tid = data.get("ticket_id")
    new_status = data.get("status")

    for c in COMPLAINTS_DB:
        if c["ticket_id"] == tid:
            c["status"] = new_status
            return jsonify({"success": True})

    return jsonify({"success": False, "message": "Ticket nahi mila"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
