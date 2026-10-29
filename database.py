"""
Database management for Digital Notice Board System
Uses standard library sqlite3 for persistent storage.
"""

import sqlite3
import os
from datetime import datetime

# Support serverless read-only environments like Vercel
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/notice_board.db"
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notice_board.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Normal',
            author TEXT NOT NULL DEFAULT 'Admin Office',
            is_pinned INTEGER NOT NULL DEFAULT 0,
            expires_at TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def seed_sample_notices():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM notices")
    count = cursor.fetchone()[0]
    
    if count == 0:
        samples = [
            (
                "Final Semester Examination Schedule Announced",
                "The Spring 2026 End-Semester Examinations will commence from May 10, 2026. Detailed subject-wise timetables and room allocations are available on the student portal. Hall tickets will be issued starting next Monday.",
                "Academic",
                "Urgent",
                "Controller of Examinations",
                1,
                "2026-05-30"
            ),
            (
                "Campus Network Maintenance Window This Weekend",
                "Please be informed that data center maintenance and Wi-Fi infrastructure upgrades will occur on Saturday from 10:00 PM to Sunday 4:00 AM. Internet access and university portal access may experience intermittent downtime.",
                "Technical",
                "High",
                "IT Infrastructure Team",
                0,
                "2026-04-20"
            ),
            (
                "Annual Tech Symposium & Hackathon Registrations Open",
                "Join us for 'InnovateX 2026' featuring 36-hour hackathons, robotics challenges, and keynote talks from leading industry researchers. Exciting prizes worth $15,000 to be won! Register your team of 2-4 members by April 25.",
                "Events",
                "Normal",
                "Student Affairs Council",
                1,
                "2026-04-25"
            ),
            (
                "Library Extended Hours During Reading Week",
                "The Central Library will remain open 24/7 starting from next Monday until the conclusion of final exams. Additional quiet study halls on the 3rd floor are now accessible. High-speed charging ports and coffee stations available.",
                "General",
                "Normal",
                "Chief Librarian",
                0,
                "2026-05-20"
            ),
            (
                "Urgent: Campus Shuttle Bus Route 3 Temporary Detour",
                "Due to pipeline repair work near North Gate, Shuttle Route 3 will be rerouted via Avenue 4 until further notice. Bus stops at North Hostel have been temporarily shifted to the Main Gymnasium plaza.",
                "Urgent",
                "Urgent",
                "Transportation Services",
                1,
                "2026-04-30"
            ),
            (
                "Faculty & Staff Research Grant Proposals (Q3 Call)",
                "The Office of Research and Development invites research project grant proposals under the Innovation Fund. Grant applications must be submitted via the internal research portal before May 15, 2026.",
                "Administrative",
                "Low",
                "Research Dean Office",
                0,
                "2026-05-15"
            )
        ]
        
        cursor.executemany("""
            INSERT INTO notices (title, content, category, priority, author, is_pinned, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, samples)
        conn.commit()
    conn.close()

def create_notice(title, content, category, priority='Normal', author='Admin', is_pinned=0, expires_at=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notices (title, content, category, priority, author, is_pinned, expires_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (title.strip(), content.strip(), category.strip(), priority, author.strip(), int(is_pinned), expires_at or None))
    notice_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_notice_by_id(notice_id)

def update_notice(notice_id, title=None, content=None, category=None, priority=None, author=None, is_pinned=None, expires_at=None, status=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    current = get_notice_by_id(notice_id)
    if not current:
        conn.close()
        return None
        
    new_title = title.strip() if title is not None else current['title']
    new_content = content.strip() if content is not None else current['content']
    new_category = category.strip() if category is not None else current['category']
    new_priority = priority if priority is not None else current['priority']
    new_author = author.strip() if author is not None else current['author']
    new_is_pinned = int(is_pinned) if is_pinned is not None else current['is_pinned']
    new_expires_at = expires_at if expires_at is not None else current['expires_at']
    new_status = status if status is not None else current['status']
    
    cursor.execute("""
        UPDATE notices
        SET title = ?, content = ?, category = ?, priority = ?, author = ?, 
            is_pinned = ?, expires_at = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_title, new_content, new_category, new_priority, new_author, new_is_pinned, new_expires_at, new_status, notice_id))
    
    conn.commit()
    conn.close()
    return get_notice_by_id(notice_id)

def delete_notice(notice_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_notice_by_id(notice_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices WHERE id = ?", (notice_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_notices(sort_by="date_desc", category="all", search=None, status="all"):
    """
    Fetch notices with dynamic sorting and filtering.
    sort_by options:
        - 'date_desc' (Newest first)
        - 'date_asc' (Oldest first)
        - 'category_asc' (Category A-Z)
        - 'priority' (Urgent -> High -> Normal -> Low)
        - 'title_asc' (Title A-Z)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM notices WHERE 1=1"
    params = []
    
    if category and category.lower() != "all":
        query += " AND LOWER(category) = LOWER(?)"
        params.append(category)
        
    if status and status.lower() != "all":
        query += " AND LOWER(status) = LOWER(?)"
        params.append(status)
        
    if search and search.strip():
        term = f"%{search.strip()}%"
        query += " AND (title LIKE ? OR content LIKE ? OR author LIKE ? OR category LIKE ?)"
        params.extend([term, term, term, term])
        
    # Sort ordering
    if sort_by == "date_asc":
        order_clause = "ORDER BY is_pinned DESC, created_at ASC, id ASC"
    elif sort_by == "category_asc":
        order_clause = "ORDER BY is_pinned DESC, category ASC, created_at DESC, id DESC"
    elif sort_by == "priority":
        order_clause = """
            ORDER BY is_pinned DESC,
            CASE priority
                WHEN 'Urgent' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Normal' THEN 3
                WHEN 'Low' THEN 4
                ELSE 5
            END ASC,
            created_at DESC,
            id DESC
        """
    elif sort_by == "title_asc":
        order_clause = "ORDER BY is_pinned DESC, title ASC, id DESC"
    else:  # default date_desc
        order_clause = "ORDER BY is_pinned DESC, created_at DESC, id DESC"
        
    query += f" {order_clause}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM notices ORDER BY category ASC")
    categories = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return categories

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM notices")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM notices WHERE priority = 'Urgent' OR category = 'Urgent'")
    urgent = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM notices WHERE is_pinned = 1")
    pinned = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT category) FROM notices")
    categories_count = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total": total,
        "urgent": urgent,
        "pinned": pinned,
        "categories_count": categories_count
    }
