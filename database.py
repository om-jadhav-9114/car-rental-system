import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bookings.db")

# -------------------- DB Connection --------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------- Init DB --------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # ---------------- bookings table ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        car_model TEXT,
        car_image TEXT,
        start_date TEXT,
        end_date TEXT,
        price TEXT,
        notes TEXT,
        payment_method TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- admins table ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # ---------------- users table (🔥 NEW SECURITY FIX) ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()

    # ---------------- default admin ----------------
    cur.execute("SELECT COUNT(*) as cnt FROM admins")
    row = cur.fetchone()
    if row and row["cnt"] == 0:
        default_username = "omjadhav"
        default_password = "om@9114"
        hashed = generate_password_hash(default_password)
        cur.execute(
            "INSERT INTO admins (username, password) VALUES (?, ?)",
            (default_username, hashed)
        )
        conn.commit()

    conn.close()


# =====================================================
# ===================== BOOKINGS ======================
# =====================================================

def add_booking(booking):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bookings
        (name, email, phone, car_model, car_image,
         start_date, end_date, price, notes, payment_method, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        booking.get("name"),
        booking.get("email"),
        booking.get("phone"),
        booking.get("car_model"),
        booking.get("car_image"),
        booking.get("start_date"),
        booking.get("end_date"),
        booking.get("price"),
        booking.get("notes"),
        booking.get("payment_method"),   
        "Pending"
    ))

    conn.commit()
    booking_id = cur.lastrowid
    conn.close()
    return booking_id


def get_bookings():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM bookings ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows


def get_booking(booking_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM bookings WHERE id = ?",
        (booking_id,)
    ).fetchone()
    conn.close()
    return row


def update_booking_status(booking_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE bookings SET status = ? WHERE id = ?",
        (status, booking_id)
    )
    conn.commit()
    conn.close()


def delete_booking(booking_id):
    conn = get_conn()
    conn.execute(
        "DELETE FROM bookings WHERE id = ?",
        (booking_id,)
    )
    conn.commit()
    conn.close()


def clear_bookings():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM bookings")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='bookings'")

    conn.commit()
    conn.close()


def get_bookings_by_user(email):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM bookings WHERE email = ? ORDER BY created_at DESC",
        (email,)
    ).fetchall()
    conn.close()
    return rows


# =====================================================
# ====================== ADMIN ========================
# =====================================================

def get_admin_by_username(username):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM admins WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()
    return row


# =====================================================
# ================= USER AUTH (🔥 FIX) =================
# =====================================================

def register_user(email, password):
    conn = get_conn()
    cur = conn.cursor()

    hashed = generate_password_hash(password)

    cur.execute(
        "INSERT INTO users (email, password) VALUES (?, ?)",
        (email, hashed)
    )

    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()
    return row


def verify_user(email, password):
    user = get_user_by_email(email)

    if user and check_password_hash(user["password"], password):
        return True
    return False
