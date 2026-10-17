import os
import random
import time
import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ==========================================
# 📧 EMAIL CONFIGURATION
# ==========================================
SENDER_EMAIL = "adarshkumar83503@gmail.com"
SENDER_APP_PASSWORD = "sfrl khsi gaso roni"

# ==========================================
# 👥 IN-MEMORY DATABASES
# ==========================================
STUDENTS_DB = {
    "25116CN001": {"name": "Adarsh", "email": "adarshkumar83503@gmail.com"},
    "25116CN407": {"name": "AKANSHA", "email": "akanshasingh16806@gmail.com"},
    "25116CN091": {"name": "Aisha", "email": "pandeyaisha829@gmail.com"},
    "25116CN029": {"name": "Aditya", "email": "aditya33322@gmail.com"}
}

OTP_STORE = {}
COMPLAINTS_DB = []

CAMPUS_DATA = {
    "library": {
        "name": "Central Library (GL Bajaj)",
        "block": "Main Academic Block",
        "floor": "Ground / 1st Floor",
        "lat": 28.4728,
        "lng": 77.4897,
        "indoor": "Main entrance se enter karein -> Right wing corridor -> Central Library.",
        "keywords": ["library", "book", "padhne", "study", "kitab"]
    },
    "canteen": {
        "name": "Campus Cafeteria & Food Court",
        "block": "Near PGDM / Hostel Area",
        "floor": "Ground Floor",
        "lat": 28.4722,
        "lng": 77.4892,
        "indoor": "Academic block ke piche garden cross karke seedha Canteen entrance.",
        "keywords": ["canteen", "food", "khana", "lunch", "cafeteria"]
    },
    "audi": {
        "name": "Main Auditorium",
        "block": "Block A",
        "floor": "Ground Floor",
        "lat": 28.4735,
        "lng": 77.4889,
        "indoor": "Main gate se left -> Block A ground floor auditorium hall.",
        "keywords": ["audi", "auditorium", "event", "seminar", "hall"]
    },
    "admin": {
        "name": "Registrar & Accounts Office",
        "block": "Administrative Block",
        "floor": "Ground Floor",
        "lat": 28.4730,
        "lng": 77.4895,
        "indoor": "Reception se seedha andar -> Counter 1-4 for fees and admission queries.",
        "keywords": ["admin", "accounts", "fees", "fee", "admission", "scholarship"]
    }
}

# ==========================================
# 🌐 MAIN ROUTE
# ==========================================
@app.route("/")
def home():
    formatted_locations = {
        k: {
            "name": v["name"],
            "lat": v["lat"],
            "lng": v["lng"],
            "desc": f"{v['block']} ({v['floor']})"
        }
        for k, v in CAMPUS_DATA.items()
    }
    return render_template("index.html", locations=formatted_locations)

# ==========================================
# 🔐 OTP AUTHENTICATION
# ==========================================
@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json or {}
    admission_no = data.get("admission_no", "").strip().upper()

    if admission_no not in STUDENTS_DB:
        return jsonify({
            "success": False,
            "message": "Admission Number record me nahi mila! (Registered: 25116CN001)"
        }), 404

    student = STUDENTS_DB[admission_no]
    recipient_email = student["email"]

    # 6-digit OTP
    otp = str(random.randint(100000, 999999))
    OTP_STORE[admission_no] = {
        "otp": otp,
        "expires": time.time() + 300
    }

    print(f"\n>>> [OTP GENERATED] Admission: {admission_no} | OTP: {otp} <<<\n", flush=True)

    # Email bhejne ki koshish (SSL Port 465)
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = "GL Bajaj Campus Guide - Your Login OTP"

        body = f"""Hello {student.get('name', 'Student')},

Aapka GL Bajaj AI Campus Guide login OTP hai: {otp}

Yeh OTP agle 5 minute ke liye valid hai.
Suraksha ke liye ise kisi ke sath share na karein.

Best regards,
GL Bajaj AI Campus Guide Team"""
        msg.attach(MIMEText(body, 'plain'))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=10) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(msg)

        return jsonify({
            "success": True,
            "message": f"OTP successfully sent to {recipient_email}!"
        })

    except Exception as e:
        print(f"\n[RENDER SMTP BLOCKED] Testing OTP generated: {otp} | Details: {e}\n", flush=True)
        # Render cloud environment ke liye clean display
        return jsonify({
            "success": True,
            "message": f"Demo Mode OTP for Verification: {otp}",
            "fallback_otp": otp
        })

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json or {}
    admission_no = data.get("admission_no", "").strip().upper()
    user_otp = data.get("otp", "").strip()

    if admission_no not in OTP_STORE:
        return jsonify({"success": False, "message": "Pehle OTP request karein."}), 400

    record = OTP_STORE[admission_no]

    if time.time() > record["expires"]:
        del OTP_STORE[admission_no]
        return jsonify({"success": False, "message": "OTP expire ho chuka hai. Dobara try karein."}), 400

    if user_otp == record["otp"]:
        del OTP_STORE[admission_no]
        student = STUDENTS_DB[admission_no]
        return jsonify({
            "success": True,
            "message": "Login safal hua!",
            "user": student
        })
    else:
        return jsonify({"success": False, "message": "Galat OTP! Kripya dobara check karein."}), 400

# ==========================================
# ⚠️ GRIEVANCE / COMPLAINT & ADMIN ROUTES
# ==========================================
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    data = request.json or {}
    admission_no = data.get("admission_no", "Guest Student")
    category = data.get("category", "General")
    location = data.get("location", "Not Specified")
    description = data.get("description", "").strip()

    if not description:
        return jsonify({"success": False, "message": "Kripya samasya ka vivaran likhein."})

    ticket_id = f"GLB-CMP-{random.randint(1000, 9999)}"
    timestamp = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    new_record = {
        "ticket_id": ticket_id,
        "admission_no": admission_no,
        "category": category,
        "location": location,
        "description": description,
        "status": "Pending Review",
        "created_at": timestamp
    }
    COMPLAINTS_DB.append(new_record)

    print(f"\n🚨 [COMPLAINT LOGGED] {ticket_id} by {admission_no} ({location}): {description}\n", flush=True)

    return jsonify({
        "success": True,
        "message": "Aapki complaint darj kar li gayi hai!",
        "ticket_id": ticket_id
    })

@app.route("/admin")
def admin_dashboard():
    return render_template("admin.html", complaints=list(reversed(COMPLAINTS_DB)))

@app.route("/api/complaints/update-status", methods=["POST"])
def update_complaint_status():
    data = request.json or {}
    ticket_id = data.get("ticket_id")
    new_status = data.get("status")

    for cmp in COMPLAINTS_DB:
        if cmp["ticket_id"] == ticket_id:
            cmp["status"] = new_status
            return jsonify({"success": True})

    return jsonify({"success": False, "message": "Ticket nahi mila"}), 404

# ==========================================
# 🚀 SERVER START
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
