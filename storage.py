import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta

DB_PATH = os.path.join("data", "app.db")


def ensure_data_dir() -> None:
    """Create the data directory if it doesn't exist."""
    os.makedirs("data", exist_ok=True)


@contextmanager
def get_connection():
    """
    Yield a SQLite connection and ensure it closes cleanly.
    """
    ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """
    Create the database tables if they do not already exist.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS terms (
                term_id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_name TEXT NOT NULL UNIQUE,
                start_date TEXT,
                end_date TEXT,
                active INTEGER NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_registry (
                registry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER NOT NULL,
                canvas_course_id TEXT NOT NULL,
                course_name TEXT NOT NULL,
                section_name TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                notes TEXT,
                FOREIGN KEY (term_id) REFERENCES terms(term_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exams (
                exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER NOT NULL,
                exam_number INTEGER NOT NULL,
                exam_name TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (term_id) REFERENCES terms(term_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slots (
                slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                location TEXT NOT NULL,
                capacity INTEGER NOT NULL DEFAULT 1,
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (exam_id) REFERENCES exams(exam_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_id INTEGER NOT NULL,
                canvas_user_id TEXT NOT NULL,
                canvas_course_id TEXT NOT NULL,
                section_id TEXT,
                status TEXT NOT NULL DEFAULT 'booked',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (slot_id) REFERENCES slots(slot_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extended_time_eligibility (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                canvas_user_id TEXT NOT NULL,
                term_id INTEGER NOT NULL,
                exam_id INTEGER,
                extra_minutes INTEGER NOT NULL DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (term_id) REFERENCES terms(term_id),
                FOREIGN KEY (exam_id) REFERENCES exams(exam_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS availability_templates (
                template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER NOT NULL,
                location TEXT NOT NULL,
                day_of_week INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (term_id) REFERENCES terms(term_id)
            )
        """)



def get_terms():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM terms ORDER BY term_name").fetchall()
        return [dict(row) for row in rows]


def add_term(term_name: str, start_date: str, end_date: str, active: int) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO terms (term_name, start_date, end_date, active)
            VALUES (?, ?, ?, ?)
        """, (term_name, start_date, end_date, active))


def get_courses():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT cr.*, t.term_name
            FROM course_registry cr
            JOIN terms t ON cr.term_id = t.term_id
            ORDER BY t.term_name, cr.course_name, cr.section_name
        """).fetchall()
        return [dict(row) for row in rows]


def add_course(term_id: int, canvas_course_id: str, course_name: str, section_name: str, notes: str) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO course_registry (term_id, canvas_course_id, course_name, section_name, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (term_id, canvas_course_id, course_name, section_name, notes))

def get_exams():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT e.*, t.term_name
            FROM exams e
            JOIN terms t ON e.term_id = t.term_id
            ORDER BY t.term_name, e.exam_number
        """).fetchall()
        return [dict(row) for row in rows]


def add_exam(term_id: int, exam_number: int, exam_name: str, active: int = 1) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO exams (term_id, exam_number, exam_name, active)
            VALUES (?, ?, ?, ?)
        """, (term_id, exam_number, exam_name, active))


def exam_exists(term_id: int, exam_number: int) -> bool:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT 1
            FROM exams
            WHERE term_id = ? AND exam_number = ?
            LIMIT 1
        """, (term_id, exam_number)).fetchone()
        return row is not None


def seed_default_lab_exams(term_id: int) -> int:
    """
    Seed Lab Exams 2-10 for a given term.
    Returns the number of exams added.
    """
    default_exams = [
        (2, "Cytology, Histology, & the Integumentary System"),
        (3, "Skeletal System"),
        (4, "Muscular System"),
        (5, "Nervous System"),
        (6, "Endocrine and Sensory Systems"),
        (7, "Circulatory System"),
        (8, "Respiratory System"),
        (9, "Digestive System"),
        (10, "Urinary and Reproductive System"),
    ]

    added_count = 0

    with get_connection() as conn:
        for exam_number, exam_name in default_exams:
            row = conn.execute("""
                SELECT 1
                FROM exams
                WHERE term_id = ? AND exam_number = ?
                LIMIT 1
            """, (term_id, exam_number)).fetchone()

            if row is None:
                conn.execute("""
                    INSERT INTO exams (term_id, exam_number, exam_name, active)
                    VALUES (?, ?, ?, 1)
                """, (term_id, exam_number, exam_name))
                added_count += 1

    return added_count

def init_availability_tables() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS availability_templates (
                template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER NOT NULL,
                location TEXT NOT NULL,
                day_of_week INTEGER NOT NULL,   -- 0=Monday, 6=Sunday
                start_time TEXT NOT NULL,       -- HH:MM
                end_time TEXT NOT NULL,         -- HH:MM
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (term_id) REFERENCES terms(term_id)
            )
        """)

def get_exam_options():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT e.exam_id, e.exam_number, e.exam_name, t.term_name
            FROM exams e
            JOIN terms t ON e.term_id = t.term_id
            WHERE e.active = 1
            ORDER BY t.term_name, e.exam_number
        """).fetchall()
        return [dict(row) for row in rows]


def add_availability_template(term_id: int, location: str, day_of_week: int, start_time: str, end_time: str) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO availability_templates (term_id, location, day_of_week, start_time, end_time, active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (term_id, location, day_of_week, start_time, end_time))


def get_availability_templates(term_id: int = None):
    with get_connection() as conn:
        if term_id is None:
            rows = conn.execute("""
                SELECT at.*, t.term_name
                FROM availability_templates at
                JOIN terms t ON at.term_id = t.term_id
                ORDER BY t.term_name, at.location, at.day_of_week, at.start_time
            """).fetchall()
        else:
            rows = conn.execute("""
                SELECT at.*, t.term_name
                FROM availability_templates at
                JOIN terms t ON at.term_id = t.term_id
                WHERE at.term_id = ?
                ORDER BY at.location, at.day_of_week, at.start_time
            """, (term_id,)).fetchall()
        return [dict(row) for row in rows]


def delete_availability_template(template_id: int) -> None:
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM availability_templates
            WHERE template_id = ?
        """, (template_id,))


def seed_default_availability(term_id: int) -> int:
    """
    Seed default location availability:
    SLO: Mon-Fri 09:00-17:00, Sat 09:00-13:00
    NCC: Mon-Fri 09:00-17:00
    """
    defaults = []

    # SLO Mon-Fri
    for day in range(0, 5):
        defaults.append((term_id, "SLO", day, "09:00", "17:00"))

    # SLO Saturday
    defaults.append((term_id, "SLO", 5, "09:00", "13:00"))

    # NCC Mon-Fri
    for day in range(0, 5):
        defaults.append((term_id, "NCC", day, "09:00", "17:00"))

    added = 0

    with get_connection() as conn:
        for row in defaults:
            exists = conn.execute("""
                SELECT 1
                FROM availability_templates
                WHERE term_id = ? AND location = ? AND day_of_week = ?
                  AND start_time = ? AND end_time = ?
                LIMIT 1
            """, row).fetchone()

            if exists is None:
                conn.execute("""
                    INSERT INTO availability_templates
                    (term_id, location, day_of_week, start_time, end_time, active)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, row)
                added += 1

    return added


def add_slot(exam_id: int, start_time: str, end_time: str, location: str, capacity: int = 1) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO slots (exam_id, start_time, end_time, location, capacity, active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (exam_id, start_time, end_time, location, capacity))


def get_slots():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT s.*, e.exam_number, e.exam_name, t.term_name
            FROM slots s
            JOIN exams e ON s.exam_id = e.exam_id
            JOIN terms t ON e.term_id = t.term_id
            ORDER BY s.start_time
        """).fetchall()
        return [dict(row) for row in rows]


def generate_slots_from_templates(
    exam_id: int,
    term_id: int,
    date_start: str,
    date_end: str,
    slot_minutes: int,
    capacity: int = 1
) -> int:
    """
    Generate slots for the given exam using availability templates
    between date_start and date_end inclusive.
    """
    with get_connection() as conn:
        templates = conn.execute("""
            SELECT *
            FROM availability_templates
            WHERE term_id = ? AND active = 1
            ORDER BY location, day_of_week, start_time
        """, (term_id,)).fetchall()

        if not templates:
            return 0

        start_date = datetime.strptime(date_start, "%Y-%m-%d").date()
        end_date = datetime.strptime(date_end, "%Y-%m-%d").date()

        added = 0
        current_date = start_date

        while current_date <= end_date:
            weekday = current_date.weekday()

            matching_templates = [t for t in templates if t["day_of_week"] == weekday]

            for template in matching_templates:
                start_dt = datetime.strptime(
                    f"{current_date} {template['start_time']}",
                    "%Y-%m-%d %H:%M"
                )
                end_dt = datetime.strptime(
                    f"{current_date} {template['end_time']}",
                    "%Y-%m-%d %H:%M"
                )

                slot_start = start_dt
                while slot_start + timedelta(minutes=slot_minutes) <= end_dt:
                    slot_end = slot_start + timedelta(minutes=slot_minutes)

                    start_iso = slot_start.strftime("%Y-%m-%d %H:%M")
                    end_iso = slot_end.strftime("%Y-%m-%d %H:%M")

                    exists = conn.execute("""
                        SELECT 1
                        FROM slots
                        WHERE exam_id = ? AND start_time = ? AND end_time = ? AND location = ?
                        LIMIT 1
                    """, (exam_id, start_iso, end_iso, template["location"])).fetchone()

                    if exists is None:
                        conn.execute("""
                            INSERT INTO slots (exam_id, start_time, end_time, location, capacity, active)
                            VALUES (?, ?, ?, ?, ?, 1)
                        """, (exam_id, start_iso, end_iso, template["location"], capacity))
                        added += 1

                    slot_start = slot_end

            current_date += timedelta(days=1)

    return added

def get_active_terms():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM terms
            WHERE active = 1
            ORDER BY term_name
        """).fetchall()
        return [dict(row) for row in rows]


def get_exams_by_term(term_id: int):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM exams
            WHERE term_id = ? AND active = 1
            ORDER BY exam_number
        """, (term_id,)).fetchall()
        return [dict(row) for row in rows]


def get_available_slots_for_exam(exam_id: int):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT s.*
            FROM slots s
            WHERE s.exam_id = ?
              AND s.active = 1
              AND (
                    SELECT COUNT(*)
                    FROM bookings b
                    WHERE b.slot_id = s.slot_id
                      AND b.status = 'booked'
                  ) < s.capacity
            ORDER BY s.start_time
        """, (exam_id,)).fetchall()
        return [dict(row) for row in rows]


def get_slot_by_id(slot_id: int):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT s.*, e.exam_id, e.exam_number, e.exam_name, e.term_id
            FROM slots s
            JOIN exams e ON s.exam_id = e.exam_id
            WHERE s.slot_id = ?
        """, (slot_id,)).fetchone()
        return dict(row) if row else None


def student_has_booking_same_exam_same_week(canvas_user_id: str, exam_id: int, slot_start_time: str):
    """
    Prevent booking more than one appointment in the same week for the same exam.
    """
    with get_connection() as conn:
        row = conn.execute("""
            SELECT b.booking_id, s.start_time
            FROM bookings b
            JOIN slots s ON b.slot_id = s.slot_id
            WHERE b.canvas_user_id = ?
              AND b.status = 'booked'
              AND s.exam_id = ?
        """, (canvas_user_id, exam_id)).fetchall()

        if not row:
            return False

        from datetime import datetime, timedelta

        target_dt = datetime.strptime(slot_start_time, "%Y-%m-%d %H:%M")
        target_week_start = target_dt.date() - timedelta(days=target_dt.weekday())
        target_week_end = target_week_start + timedelta(days=6)

        for existing in row:
            existing_dt = datetime.strptime(existing["start_time"], "%Y-%m-%d %H:%M")
            if target_week_start <= existing_dt.date() <= target_week_end:
                return True

        return False


def create_booking(slot_id: int, canvas_user_id: str, canvas_course_id: str = "", section_id: str = ""):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO bookings (slot_id, canvas_user_id, canvas_course_id, section_id, status)
            VALUES (?, ?, ?, ?, 'booked')
        """, (slot_id, canvas_user_id, canvas_course_id, section_id))

def get_all_bookings():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                b.booking_id,
                b.canvas_user_id,
                b.canvas_course_id,
                b.section_id,
                b.status,
                b.created_at,
                b.updated_at,
                s.slot_id,
                s.start_time,
                s.end_time,
                s.location,
                e.exam_id,
                e.exam_number,
                e.exam_name,
                t.term_id,
                t.term_name
            FROM bookings b
            JOIN slots s ON b.slot_id = s.slot_id
            JOIN exams e ON s.exam_id = e.exam_id
            JOIN terms t ON e.term_id = t.term_id
            ORDER BY s.start_time
        """).fetchall()
        return [dict(row) for row in rows]


def cancel_booking(booking_id: int) -> None:
    with get_connection() as conn:
        conn.execute("""
            UPDATE bookings
            SET status = 'cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE booking_id = ?
        """, (booking_id,))


def get_booking_by_id(booking_id: int):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                b.booking_id,
                b.canvas_user_id,
                b.canvas_course_id,
                b.section_id,
                b.status,
                b.created_at,
                b.updated_at,
                s.slot_id,
                s.start_time,
                s.end_time,
                s.location,
                e.exam_id,
                e.exam_number,
                e.exam_name,
                t.term_id,
                t.term_name
            FROM bookings b
            JOIN slots s ON b.slot_id = s.slot_id
            JOIN exams e ON s.exam_id = e.exam_id
            JOIN terms t ON e.term_id = t.term_id
            WHERE b.booking_id = ?
        """, (booking_id,)).fetchone()
        return dict(row) if row else None
