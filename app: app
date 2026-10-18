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
app.secret_key = os.environ.get("SECRET_KEY", "glbajaj_super_secret_2026")

ADMIN_PASSCODE = "GLB@ADMIN2026"
SENDER_EMAIL = "adarshkumar83503@gmail.com"
SENDER_APP_PASSWORD = "sfrl khsi gaso roni"

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
COMPLAINTS_DB = []
VISITORS_DB = []

@app.route("/")
def index():
    return render_template("index.html", locations=CAMPUS_DATA)

# ---------------- Student Auth ----------------
@app.route("/student/send-otp", methods=["POST"])
def student_send_otp():
    try:
        data = request.get_json(force=True) or {}
        adm = str(data.get("admission_no", "")).strip().upper()

        if adm not in STUDENTS_DB:
            return jsonify({"success": False, "message": "Admission ID record me nahi mila! (Use: 25116CN001)"}), 404

        student = STUDENTS_DB[adm]
        recipient_email = student["email"]
        otp = str(random.randint(100000, 999999))
        STUDENT_OTP_STORE[adm] = {"otp": otp, "expires": time.time() + 300}

        print(f"\n[OTP GENERATED] {adm} -> {otp}\n", flush=True)

        email_sent = False
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = "GL Bajaj Campus Guide - Login Verification OTP"
            body = f"Namaste {student['name']},\n\nAapka login OTP hai: {otp}\nValid for 5 minutes."
            msg.attach(MIMEText(body, 'plain'))

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=4) as server:
                server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
                server.send_message(msg)
            email_sent = True
        except Exception as err:
            print(f"[SMTP Blocked/Timeout] {err}", flush=True)

        return jsonify({
            "success": True,
            "email_sent": email_sent,
            "message": f"Verification OTP: {otp}",
            "otp": otp,
            "student_name": student["name"]
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route("/student/verify-otp", methods=["POST"])
def student_verify_otp():
    try:
        data = request.get_json(force=True) or {}
        adm = str(data.get("admission_no", "")).strip().upper()
        user_otp = str(data.get("otp", "")).strip()

        if adm not in STUDENT_OTP_STORE:
            return jsonify({"success": False, "message": "Pehle OTP generate karein."}), 400

        if user_otp == STUDENT_OTP_STORE[adm]["otp"]:
            del STUDENT_OTP_STORE[adm]
            session["user_type"] = "student"
            return jsonify({"success": True, "user": STUDENTS_DB[adm]})

        return jsonify({"success": False, "message": "Galat OTP! Dobara check karein."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ---------------- Visitor Auth ----------------
@app.route("/visitor/send-otp", methods=["POST"])
def visitor_send_otp():
    try:
        data = request.get_json(force=True) or {}
        name = str(data.get("name", "")).strip()
        mobile = str(data.get("mobile", "")).strip()
        aadhaar = str(data.get("aadhaar", "")).strip()
        purpose = str(data.get("purpose", "")).strip()

        if not name or not mobile or not aadhaar or not purpose:
            return jsonify({"success": False, "message": "Saare fields bharein."}), 400

        otp = str(random.randint(100000, 999999))
        VISITOR_OTP_STORE[mobile] = {
            "otp": otp,
            "name": name,
            "mobile": mobile,
            "masked_aadhaar": "[Aadhaar Redacted]",
            "purpose": purpose,
            "expires": time.time() + 300
        }

        print(f"\n[VISITOR OTP] {mobile} -> {otp}\n", flush=True)
        return jsonify({"success": True, "message": f"Verification OTP: {otp}", "otp": otp})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/visitor/verify-otp", methods=["POST"])
def visitor_verify_otp():
    try:
        data = request.get_json(force=True) or {}
        mobile = str(data.get("mobile", "")).strip()
        user_otp = str(data.get("otp", "")).strip()

        if mobile not in VISITOR_OTP_STORE:
            return jsonify({"success": False, "message": "OTP expire ho gaya."}), 400

        rec = VISITOR_OTP_STORE[mobile]
        if user_otp == rec["otp"]:
            pass_id = f"GP-{random.randint(1000, 9999)}"
            entry = {
                "pass_id": pass_id,
                "name": rec["name"],
                "mobile": rec["mobile"],
                "masked_aadhaar": rec["masked_aadhaar"],
                "purpose": rec["purpose"],
                "entry_time": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "status": "Checked In"
            }
            VISITORS_DB.append(entry)
            del VISITOR_OTP_STORE[mobile]
            return jsonify({"success": True, "message": "Gate Pass ready!", "visitor": entry})

        return jsonify({"success": False, "message": "Galat OTP!"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ---------------- Grievance & Admin ----------------
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    try:
        data = request.get_json(force=True) or {}
        desc = str(data.get("description", "")).strip()
        if not desc:
            return jsonify({"success": False, "message": "Vivaran zaroori hai."}), 400

        tid = f"GLB-{random.randint(1000, 9999)}"
        entry = {
            "ticket_id": tid,
            "admission_no": data.get("admission_no", "Guest"),
            "category": data.get("category", "General"),
            "location": data.get("location", "Campus"),
            "description": desc,
            "status": "Pending",
            "created_at": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
        }
        COMPLAINTS_DB.append(entry)
        return jsonify({"success": True, "message": "Complaint darj ho gayi!", "ticket_id": tid})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/admin", methods=["GET", "POST"])
def admin_portal():
    if request.method == "POST":
        if request.form.get("passcode", "").strip() == ADMIN_PASSCODE:
            session["is_team_admin"] = True
        else:
            return render_template("admin.html", authenticated=False, error="Galat Passcode! Access Denied.")

    return render_template("admin.html",
                           authenticated=session.get("is_team_admin", False),
                           complaints=list(reversed(COMPLAINTS_DB)),
                           visitors=list(reversed(VISITORS_DB)))

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_team_admin", None)
    return render_template("admin.html", authenticated=False, error="Logged out.")

@app.route("/api/complaints/update-status", methods=["POST"])
def update_status():
    if not session.get("is_team_admin"):
        return jsonify({"success": False}), 403
    data = request.get_json(force=True) or {}
    for c in COMPLAINTS_DB:
        if c["ticket_id"] == data.get("ticket_id"):
            c["status"] = data.get("status")
            return jsonify({"success": True})
    return jsonify({"success": False}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)import os
import random
import time
import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "glbajaj_super_secret_2026")

ADMIN_PASSCODE = "GLB@ADMIN2026"
SENDER_EMAIL = "adarshkumar83503@gmail.com"
SENDER_APP_PASSWORD = "sfrl khsi gaso roni"

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
COMPLAINTS_DB = []
VISITORS_DB = []

@app.route("/")
def index():
    return render_template("index.html", locations=CAMPUS_DATA)

# ---------------- Student Auth ----------------
@app.route("/student/send-otp", methods=["POST"])
def student_send_otp():
    try:
        data = request.get_json(force=True) or {}
        adm = str(data.get("admission_no", "")).strip().upper()

        if adm not in STUDENTS_DB:
            return jsonify({"success": False, "message": "Admission ID record me nahi mila! (Use: 25116CN001)"}), 404

        student = STUDENTS_DB[adm]
        recipient_email = student["email"]
        otp = str(random.randint(100000, 999999))
        STUDENT_OTP_STORE[adm] = {"otp": otp, "expires": time.time() + 300}

        print(f"\n[OTP GENERATED] {adm} -> {otp}\n", flush=True)

        email_sent = False
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = "GL Bajaj Campus Guide - Login Verification OTP"
            body = f"Namaste {student['name']},\n\nAapka login OTP hai: {otp}\nValid for 5 minutes."
            msg.attach(MIMEText(body, 'plain'))

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=4) as server:
                server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
                server.send_message(msg)
            email_sent = True
        except Exception as err:
            print(f"[SMTP Blocked/Timeout] {err}", flush=True)

        return jsonify({
            "success": True,
            "email_sent": email_sent,
            "message": f"Verification OTP: {otp}",
            "otp": otp,
            "student_name": student["name"]
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route("/student/verify-otp", methods=["POST"])
def student_verify_otp():
    try:
        data = request.get_json(force=True) or {}
        adm = str(data.get("admission_no", "")).strip().upper()
        user_otp = str(data.get("otp", "")).strip()

        if adm not in STUDENT_OTP_STORE:
            return jsonify({"success": False, "message": "Pehle OTP generate karein."}), 400

        if user_otp == STUDENT_OTP_STORE[adm]["otp"]:
            del STUDENT_OTP_STORE[adm]
            session["user_type"] = "student"
            return jsonify({"success": True, "user": STUDENTS_DB[adm]})

        return jsonify({"success": False, "message": "Galat OTP! Dobara check karein."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ---------------- Visitor Auth ----------------
@app.route("/visitor/send-otp", methods=["POST"])
def visitor_send_otp():
    try:
        data = request.get_json(force=True) or {}
        name = str(data.get("name", "")).strip()
        mobile = str(data.get("mobile", "")).strip()
        aadhaar = str(data.get("aadhaar", "")).strip()
        purpose = str(data.get("purpose", "")).strip()

        if not name or not mobile or not aadhaar or not purpose:
            return jsonify({"success": False, "message": "Saare fields bharein."}), 400

        otp = str(random.randint(100000, 999999))
        VISITOR_OTP_STORE[mobile] = {
            "otp": otp,
            "name": name,
            "mobile": mobile,
            "masked_aadhaar": "[Aadhaar Redacted]",
            "purpose": purpose,
            "expires": time.time() + 300
        }

        print(f"\n[VISITOR OTP] {mobile} -> {otp}\n", flush=True)
        return jsonify({"success": True, "message": f"Verification OTP: {otp}", "otp": otp})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/visitor/verify-otp", methods=["POST"])
def visitor_verify_otp():
    try:
        data = request.get_json(force=True) or {}
        mobile = str(data.get("mobile", "")).strip()
        user_otp = str(data.get("otp", "")).strip()

        if mobile not in VISITOR_OTP_STORE:
            return jsonify({"success": False, "message": "OTP expire ho gaya."}), 400

        rec = VISITOR_OTP_STORE[mobile]
        if user_otp == rec["otp"]:
            pass_id = f"GP-{random.randint(1000, 9999)}"
            entry = {
                "pass_id": pass_id,
                "name": rec["name"],
                "mobile": rec["mobile"],
                "masked_aadhaar": rec["masked_aadhaar"],
                "purpose": rec["purpose"],
                "entry_time": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "status": "Checked In"
            }
            VISITORS_DB.append(entry)
            del VISITOR_OTP_STORE[mobile]
            return jsonify({"success": True, "message": "Gate Pass ready!", "visitor": entry})

        return jsonify({"success": False, "message": "Galat OTP!"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ---------------- Grievance & Admin ----------------
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    try:
        data = request.get_json(force=True) or {}
        desc = str(data.get("description", "")).strip()
        if not desc:
            return jsonify({"success": False, "message": "Vivaran zaroori hai."}), 400

        tid = f"GLB-{random.randint(1000, 9999)}"
        entry = {
            "ticket_id": tid,
            "admission_no": data.get("admission_no", "Guest"),
            "category": data.get("category", "General"),
            "location": data.get("location", "Campus"),
            "description": desc,
            "status": "Pending",
            "created_at": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
        }
        COMPLAINTS_DB.append(entry)
        return jsonify({"success": True, "message": "Complaint darj ho gayi!", "ticket_id": tid})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/admin", methods=["GET", "POST"])
def admin_portal():
    if request.method == "POST":
        if request.form.get("passcode", "").strip() == ADMIN_PASSCODE:
            session["is_team_admin"] = True
        else:
            return render_template("admin.html", authenticated=False, error="Galat Passcode! Access Denied.")

    return render_template("admin.html",
                           authenticated=session.get("is_team_admin", False),
                           complaints=list(reversed(COMPLAINTS_DB)),
                           visitors=list(reversed(VISITORS_DB)))

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_team_admin", None)
    return render_template("admin.html", authenticated=False, error="Logged out.")

@app.route("/api/complaints/update-status", methods=["POST"])
def update_status():
    if not session.get("is_team_admin"):
        return jsonify({"success": False}), 403
    data = request.get_json(force=True) or {}
    for c in COMPLAINTS_DB:
        if c["ticket_id"] == data.get("ticket_id"):
            c["status"] = data.get("status")
            return jsonify({"success": True})
    return jsonify({"success": False}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
