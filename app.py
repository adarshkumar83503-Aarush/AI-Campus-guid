import os
import random
import time
import datetime
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = "gl_bajaj_campus_super_secret_key_2026"

# ==========================================
# 🔐 ADMIN CREDENTIALS (Only for Team Members)
# ==========================================
ADMIN_PASSCODE = "GLB@ADMIN2026"

# ==========================================
# 📍 CAMPUS LOCATIONS DATA
# ==========================================
CAMPUS_DATA = {
    "ab1": {
        "name": "Academic Block 1 (AB-1)",
        "lat": 28.4725,
        "lng": 77.4891,
        "desc": "First Year Classes, Dean Office & Lecture Halls"
    },
    "ab2": {
        "name": "Academic Block 2 (AB-2)",
        "lat": 28.4728,
        "lng": 77.4896,
        "desc": "CSE, IT, AI & Data Science Labs"
    },
    "library": {
        "name": "Central Knowledge Park Library",
        "lat": 28.4730,
        "lng": 77.4894,
        "desc": "Research Wing & Reading Halls"
    },
    "audi": {
        "name": "Mahatma Gandhi Central Auditorium",
        "lat": 28.4735,
        "lng": 77.4889,
        "desc": "Air-conditioned 1000+ Capacity Hall"
    },
    "cafeteria": {
        "name": "Student Cafeteria & Food Court",
        "lat": 28.4721,
        "lng": 77.4890,
        "desc": "Cafeteria & Open Dining Courtyard"
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

COMPLAINTS_DB = [
    {
        "ticket_id": "GLB-101",
        "admission_no": "25116CN001",
        "category": "Lab & Hardware",
        "location": "AB-2, IoT Lab 3",
        "description": "Ethernet switch power issue at Bench 2.",
        "status": "In Progress",
        "created_at": "18 Oct 2026, 09:30 AM"
    }
]

VISITORS_DB = [
    {
        "pass_id": "GP-8801",
        "name": "Ramesh Sharma",
        "mobile": "9876543210",
        "masked_aadhaar": "XXXX-XXXX-1234",
        "purpose": "Admission Enquiry for B.Tech CSE",
        "entry_time": "18 Oct 2026, 10:15 AM",
        "status": "Checked In"
    }
]

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
        return jsonify({"success": False, "message": "Admission ID nahi mili! (Try: 25116CN001)"}), 404

    otp = str(random.randint(100000, 999999))
    STUDENT_OTP_STORE[adm] = {"otp": otp, "expires": time.time() + 300}
    print(f"\n[STUDENT OTP] {adm} -> {otp}\n", flush=True)

    return jsonify({
        "success": True,
        "message": f"Verification OTP: {otp}",
        "otp": otp,
        "student_name": STUDENTS_DB[adm]["name"]
    })

@app.route("/student/verify-otp", methods=["POST"])
def student_verify_otp():
    data = request.json or {}
    adm = data.get("admission_no", "").strip().upper()
    user_otp = data.get("otp", "").strip()

    if adm not in STUDENT_OTP_STORE:
        return jsonify({"success": False, "message": "Pehle OTP request karein."}), 400

    if user_otp == STUDENT_OTP_STORE[adm]["otp"]:
        del STUDENT_OTP_STORE[adm]
        session["user_type"] = "student"
        session["user_id"] = adm
        return jsonify({"success": True, "user": STUDENTS_DB[adm]})

    return jsonify({"success": False, "message": "Galat OTP! Kripya dobara check karein."}), 400

# ------------------------------------------
# 🪪 2. VISITOR GATE PASS & REGISTRATION
# ------------------------------------------
@app.route("/visitor/send-otp", methods=["POST"])
def visitor_send_otp():
    data = request.json or {}
    name = data.get("name", "").strip()
    mobile = data.get("mobile", "").strip()
    aadhaar = data.get("aadhaar", "").strip()
    purpose = data.get("purpose", "").strip()

    if not name or not mobile or not aadhaar or not purpose:
        return jsonify({"success": False, "message": "Kripya Naam, Aadhaar, Mobile aur Purpose saare fields bharein."}), 400

    if len(mobile) < 10:
        return jsonify({"success": False, "message": "Kripya 10-digit mobile number daalein."}), 400

    otp = str(random.randint(100000, 999999))
    
    # Store temporary session data before OTP verification
    VISITOR_OTP_STORE[mobile] = {
        "otp": otp,
        "name": name,
        "mobile": mobile,
        # Secure display mask for government ID
        "masked_aadhaar": f"XXXX-XXXX-{aadhaar[-4:]}" if len(aadhaar) >= 4 else "[Aadhaar Redacted]",
        "purpose": purpose,
        "expires": time.time() + 300
    }

    print(f"\n[VISITOR OTP] Mobile: {mobile} | Purpose: {purpose} | OTP: {otp}\n", flush=True)

    return jsonify({
        "success": True,
        "message": f"Visitor Verification OTP: {otp}",
        "otp": otp
    })

@app.route("/visitor/verify-otp", methods=["POST"])
def visitor_verify_otp():
    data = request.json or {}
    mobile = data.get("mobile", "").strip()
    user_otp = data.get("otp", "").strip()

    if mobile not in VISITOR_OTP_STORE:
        return jsonify({"success": False, "message": "OTP record nahi mila ya expire ho gaya."}), 400

    record = VISITOR_OTP_STORE[mobile]

    if user_otp == record["otp"]:
        pass_id = f"GP-{random.randint(1000, 9999)}"
        entry_timestamp = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

        visitor_entry = {
            "pass_id": pass_id,
            "name": record["name"],
            "mobile": record["mobile"],
            "masked_aadhaar": record["masked_aadhaar"],
            "purpose": record["purpose"],
            "entry_time": entry_timestamp,
            "status": "Checked In"
        }
        
        # Add automatically to Visitors Database
        VISITORS_DB.append(visitor_entry)
        del VISITOR_OTP_STORE[mobile]

        session["user_type"] = "visitor"
        session["pass_id"] = pass_id

        return jsonify({
            "success": True,
            "message": "Gate Pass Successfully Generated!",
            "visitor": visitor_entry
        })

    return jsonify({"success": False, "message": "Galat OTP! Kripya dobara try karein."}), 400

# ------------------------------------------
# ⚠️ 3. COMPLAINTS ROUTES
# ------------------------------------------
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    data = request.json or {}
    desc = data.get("description", "").strip()
    if not desc:
        return jsonify({"success": False, "message": "Kripya samasya ka vivaran likhein."}), 400

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
    return jsonify({"success": True, "message": "Complaint safaltapoorvak darj hui!", "ticket_id": tid})

# ------------------------------------------
# 🔐 4. ADMIN DASHBOARD (Protected)
# ------------------------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin_portal():
    # Passcode verification for Team Members
    if request.method == "POST":
        entered_pass = request.form.get("passcode", "").strip()
        if entered_pass == ADMIN_PASSCODE:
            session["is_admin"] = True
        else:
            return render_template("admin.html", authenticated=False, error="Invalid Team Passcode! Access Denied.")

    is_auth = session.get("is_admin", False)
    return render_template("admin.html", 
                           authenticated=is_auth, 
                           complaints=list(reversed(COMPLAINTS_DB)), 
                           visitors=list(reversed(VISITORS_DB)))

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return render_template("admin.html", authenticated=False, error="Successfully logged out.")

@app.route("/api/complaints/update-status", methods=["POST"])
def update_complaint_status():
    if not session.get("is_admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.json or {}
    tid = data.get("ticket_id")
    new_status = data.get("status")

    for c in COMPLAINTS_DB:
        if c["ticket_id"] == tid:
            c["status"] = new_status
            return jsonify({"success": True})

    return jsonify({"success": False, "message": "Ticket not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
