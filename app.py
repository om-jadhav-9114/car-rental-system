from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import database
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# -------------------- Secret Key --------------------
app.secret_key = os.environ.get("om_SECRET_KEY", "dev-secret-123")

# -------------------- Initialize Database --------------------
database.init_db()

# =====================================================
# ===================== PUBLIC PAGES ==================
# =====================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/book")
def book():
    if "user" not in session:
        return redirect(url_for("user_sign_in"))
    return render_template("book.html")


@app.route("/pay")
def pay():
    return render_template("pay.html")


@app.route("/rate", methods=["GET", "POST"])
def rate():
    if request.method == "POST":
        rating = request.form.get("rating")
        feedback = request.form.get("feedback")

        print("Rating:", rating)
        print("Feedback:", feedback)

        flash("Rating submitted successfully!", "success")
        return redirect(url_for("rate"))

    return render_template("rate.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# =====================================================
# ================= USER AUTH =========================
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            database.register_user(email, password)
            session["user"] = email
            return redirect(url_for("book"))
        except Exception:
            return render_template("register.html", error="User already exists")

    return render_template("register.html")


@app.route("/sign_in", methods=["GET", "POST"])
def user_sign_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if database.verify_user(email, password):
            session["user"] = email
            return redirect(url_for("book"))
        else:
            return render_template("sign_in.html", error="Invalid email or password")

    return render_template("sign_in.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    session.pop("admin_username", None)
    session.pop("user", None)
    return redirect(url_for("index"))


# =====================================================
# ================= ADMIN AUTH ========================
# =====================================================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        admin = database.get_admin_by_username(username)

        if admin and check_password_hash(admin["password"], password):
            session["admin"] = True
            session["admin_username"] = username
            return redirect(url_for("admin_data"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# =====================================================
# ================= ADMIN PAGES =======================
# =====================================================

@app.route("/admin/bookings")
def admin_data():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    bookings = database.get_bookings()
    return render_template("data.html", bookings=bookings)


# =====================================================
# ================= BOOKINGS API ======================
# =====================================================

@app.route("/api/bookings", methods=["GET", "POST"])
def api_bookings():
    # -------- GET (Admin list bookings) --------
    if request.method == "GET":
        if not session.get("admin"):
            return jsonify({"error": "unauthorized"}), 401

        rows = database.get_bookings()
        bookings = [dict(row) for row in rows]
        return jsonify(bookings)

    # -------- POST (User add booking) --------
    data = request.json or {}

    booking = {
    "name": data.get("name"),
    "email": session.get("user"),   # ✅ FIX
    "phone": data.get("phone"),
    "car_model": data.get("car_model"),
    "car_image": data.get("car_image", "no-image.png"),
    "start_date": data.get("start_date"),
    "end_date": data.get("end_date"),
    "price": data.get("price"),
    "notes": data.get("notes"),
    "payment_method": data.get("payment_method", "Pending")
}

    booking_id = database.add_booking(booking)
    return jsonify({"success": True, "id": booking_id})


@app.route("/api/bookings/confirm/<int:booking_id>", methods=["POST"])
def confirm_booking(booking_id):
    if not session.get("admin"):
        return jsonify({"error": "unauthorized"}), 401

    database.update_booking_status(booking_id, "Confirmed")
    return jsonify({"success": True, "status": "Confirmed"})


@app.route("/api/bookings/reject/<int:booking_id>", methods=["POST"])
def reject_booking(booking_id):
    if not session.get("admin"):
        return jsonify({"error": "unauthorized"}), 401

    database.update_booking_status(booking_id, "Rejected")
    return jsonify({"success": True, "status": "Rejected"})


@app.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
def api_delete_booking(booking_id):
    if not session.get("admin"):
        return jsonify({"error": "unauthorized"}), 401

    database.delete_booking(booking_id)
    return jsonify({"success": True})


@app.route("/api/bookings/clear", methods=["POST"])
def api_clear_bookings():
    if not session.get("admin"):
        return jsonify({"error": "unauthorized"}), 401

    database.clear_bookings()
    return jsonify({"success": True})


# =====================================================
# ================= USER BOOKINGS =====================
# =====================================================

@app.route("/my_bookings")
def my_bookings():
    if "user" not in session:
        return redirect(url_for("user_sign_in"))

    email = session["user"]
    bookings = database.get_bookings_by_user(email)
    return render_template("my_bookings.html", bookings=bookings)


# =====================================================
# ================= RUN SERVER ========================
# =====================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)