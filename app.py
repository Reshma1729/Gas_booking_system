from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
import bcrypt
from datetime import datetime, date, timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gas_booking_system"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        password = bcrypt.hashpw(request.form["password"].encode('utf-8'), bcrypt.gensalt())
        aadhaar = request.form["aadhaar"]
        pincode = request.form["pincode"]
        address = request.form["address"]

        try:
            cursor.execute("""
                INSERT INTO users (name, phone, password, aadhaar, pincode, address)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, phone, password, aadhaar, pincode, address))
            db.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            flash("Phone number already registered! Try with another one.", "error")
            return redirect(url_for("register"))

    return render_template("login.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"].encode('utf-8')

        cursor.execute("SELECT * FROM users WHERE phone=%s", (phone,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password, user["password"].encode('utf-8')):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["pincode"] = user["pincode"]
            flash(f"Welcome {user['name']}!", "success")
            return redirect(url_for("booking"))
        else:
            flash("Invalid phone number or password!", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

# ---------------- BOOKING ----------------
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if "user_id" not in session:
        flash("Please login first!", "error")
        return redirect(url_for("login"))

    today = date.today().isoformat()
    user_pincode = session.get("pincode")

    # Fetch saved address
    cursor.execute("SELECT address FROM users WHERE id = %s", (session["user_id"],))
    user_address_row = cursor.fetchone()
    user_address = user_address_row["address"] if user_address_row else ""

    otp_sent = False

    if request.method == "POST":
        booking_type = request.form["booking_type"]

        # ----- OTP Verification -----
        if booking_type == "call_otp":
            entered_otp = request.form.get("otp")
            sent_otp = session.get("call_otp")

            if entered_otp == sent_otp:
                company = session.get("call_company", "LPG Cylinder")
                pincode = session.get("call_pincode", user_pincode)
                delivery_address = session.get("call_address", user_address)

                cursor.execute("""
                    INSERT INTO bookings (user_id, pincode, company, booking_date, delivery_address)
                    VALUES (%s, %s, %s, %s, %s)
                """, (session["user_id"], pincode, company, today, delivery_address))
                db.commit()
                booking_id = cursor.lastrowid

                flash("Booking confirmed successfully! Next booking will be available after 15 days.", "success")

                # Clear session OTP values
                for key in ["call_otp", "call_company", "call_pincode", "call_address"]:
                    session.pop(key, None)

                return redirect(url_for("payment", booking_id=booking_id))
            else:
                flash("Incorrect OTP! Please try again.", "error")
                otp_sent = True

        # ----- Generate OTP for Call Booking -----
        elif booking_type == "call":
            otp = "1234"
            session["call_otp"] = otp
            session["call_company"] = request.form.get("company")
            session["call_pincode"] = request.form.get("pincode", user_pincode)
            session["call_address"] = request.form.get("delivery_address")

            flash(f"OTP sent to your mobile number: {session.get('phone', 'XXXXXXX')}", "info")
            otp_sent = True

        # ----- Direct Booking -----
        elif booking_type == "confirm":
            company = request.form["company"]
            pincode = request.form.get("pincode", user_pincode)
            delivery_address = request.form["delivery_address"]
            booking_date = request.form["booking_date"]

            cursor.execute("""
                INSERT INTO bookings (user_id, pincode, company, booking_date, delivery_address)
                VALUES (%s, %s, %s, %s, %s)
            """, (session["user_id"], pincode, company, booking_date, delivery_address))
            db.commit()
            booking_id = cursor.lastrowid

            flash("Booking confirmed successfully! Next booking will be available after 15 days.", "success")
            return redirect(url_for("payment", booking_id=booking_id))

    return render_template(
        "booking.html",
        today=today,
        user_address=user_address,
        pincode=user_pincode,
        user_name=session.get("user_name"),
        otp_sent=otp_sent
    )

# ---------------- PAYMENT ----------------
@app.route("/payment", methods=["GET", "POST"])
def payment():
    if "user_id" not in session:
        flash("Please login first!", "error")
        return redirect(url_for("login"))

    # Get booking_id from GET or POST
    booking_id = request.args.get("booking_id") or request.form.get("booking_id")
    if not booking_id:
        flash("No booking selected for payment!", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        payment_type = request.form["payment_type"]
        amount = request.form["amount"]

        # Optional fields
        card_number = request.form.get("cardNumber") or None
        expiry_date = request.form.get("expiryDate") or None
        cvv = request.form.get("cvv") or None
        upi_id = request.form.get("upiId") or None

        cursor.execute("""
            INSERT INTO payments 
            (booking_id, payment_type, card_number, expiry_date, cvv, upi_id, status, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, payment_type, card_number, expiry_date, cvv, upi_id, "Paid", amount))
        db.commit()

        # ✅ Instead of redirecting immediately, render a success page with redirect delay
        return render_template("payment_success.html", booking_id=booking_id)

    # GET request: render payment form
    return render_template("payment.html", booking_id=booking_id)

# ---------------- DASHBOARD ----------------
from datetime import timedelta, datetime

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first!", "error")
        return redirect(url_for("login"))

    cursor.execute("""
        SELECT b.*, p.payment_type, p.amount, p.status, p.booking_id
        FROM bookings b
        LEFT JOIN payments p ON b.id = p.booking_id
        WHERE b.user_id = %s
    """, (session["user_id"],))
    bookings = cursor.fetchall()

    # Calculate delivery date (2 days after booking) if not stored
    for b in bookings:
        # Convert string with time to datetime
        if isinstance(b["booking_date"], str):
            b["booking_date"] = datetime.strptime(b["booking_date"], "%Y-%m-%d %H:%M:%S")
        
        # Calculate delivery date if not present
        if not b.get("delivery_date") or b["delivery_date"] in ("", None):
            b["delivery_date"] = b["booking_date"] + timedelta(days=2)
        else:
            if isinstance(b["delivery_date"], str):
                b["delivery_date"] = datetime.strptime(b["delivery_date"], "%Y-%m-%d %H:%M:%S")

    return render_template("dashboard.html", bookings=bookings, user_name=session.get("user_name"))


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
