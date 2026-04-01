import os
import sqlite3
from contextlib import contextmanager

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
