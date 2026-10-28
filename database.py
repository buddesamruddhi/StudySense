import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import date, datetime

DB_PATH = Path(__file__).parent / "study_analyzer.db"

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            daily_limit REAL DEFAULT 5,
            session_minutes INTEGER DEFAULT 45,
            break_minutes INTEGER DEFAULT 10,
            planning_days INTEGER DEFAULT 7,
            theme TEXT DEFAULT 'Light',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS study_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            study_date TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            planned_hours REAL DEFAULT 0,
            actual_hours REAL DEFAULT 0,
            tasks_assigned INTEGER DEFAULT 0,
            tasks_completed INTEGER DEFAULT 0,
            sleep_hours REAL DEFAULT 0,
            study_method TEXT DEFAULT 'Practice',
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            normalized_title TEXT NOT NULL,
            description TEXT DEFAULT '',
            subject TEXT DEFAULT '',
            category TEXT DEFAULT 'Assignment',
            scheduled_date TEXT NOT NULL,
            start_time TEXT DEFAULT '',
            end_time TEXT DEFAULT '',
            deadline TEXT DEFAULT '',
            priority TEXT DEFAULT 'Medium',
            estimated_duration REAL DEFAULT 1,
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            UNIQUE(user_id, normalized_title)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            pinned INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS plans(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_date TEXT NOT NULL,
            subject TEXT NOT NULL,
            task_title TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration REAL NOT NULL,
            status TEXT DEFAULT 'Planned',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        # Safe additive migrations for older versions.
        migrations = {
            "users": {
                "daily_limit": "REAL DEFAULT 5", "session_minutes": "INTEGER DEFAULT 45",
                "break_minutes": "INTEGER DEFAULT 10", "planning_days": "INTEGER DEFAULT 7",
                "theme": "TEXT DEFAULT 'Light'"
            },
            "tasks": {
                "normalized_title": "TEXT DEFAULT ''", "description": "TEXT DEFAULT ''",
                "subject": "TEXT DEFAULT ''", "category": "TEXT DEFAULT 'Assignment'",
                "scheduled_date": "TEXT DEFAULT ''", "start_time": "TEXT DEFAULT ''",
                "end_time": "TEXT DEFAULT ''", "deadline": "TEXT DEFAULT ''",
                "priority": "TEXT DEFAULT 'Medium'", "estimated_duration": "REAL DEFAULT 1",
                "status": "TEXT DEFAULT 'Pending'", "updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP"
            },
            "notes": {"category": "TEXT DEFAULT 'General'", "pinned": "INTEGER DEFAULT 0",
                      "updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP"},
            "study_logs": {"study_method": "TEXT DEFAULT 'Practice'", "notes": "TEXT DEFAULT ''"}
        }
        for table, cols in migrations.items():
            existing = {r["name"] for r in c.execute(f"PRAGMA table_info({table})").fetchall()}
            for name, definition in cols.items():
                if name not in existing:
                    c.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
        # Backfill normalized titles for pre-existing task rows.
        rows = c.execute("SELECT id,title,user_id,normalized_title FROM tasks").fetchall()
        for r in rows:
            if not r["normalized_title"]:
                norm = " ".join((r["title"] or "").lower().split())
                c.execute("UPDATE tasks SET normalized_title=? WHERE id=?", (norm, r["id"]))

def query(sql, params=()):
    with get_conn() as c:
        return [dict(r) for r in c.execute(sql, params).fetchall()]

def execute(sql, params=()):
    with get_conn() as c:
        cur = c.execute(sql, params)
        return cur.lastrowid

def user_by_email(email):
    rows = query("SELECT * FROM users WHERE lower(email)=lower(?)", (email.strip(),))
    return rows[0] if rows else None

def create_user(full_name, email, password_hash):
    return execute("INSERT INTO users(full_name,email,password_hash) VALUES(?,?,?)",
                   (full_name.strip(), email.strip().lower(), password_hash))

def get_user(user_id):
    rows = query("SELECT * FROM users WHERE id=?", (user_id,))
    return rows[0] if rows else None

def list_tasks(user_id):
    return query("SELECT * FROM tasks WHERE user_id=? ORDER BY scheduled_date, deadline, priority", (user_id,))

def save_task(user_id, data, task_id=None):
    title = data["title"].strip()
    normalized = " ".join(title.lower().split())
    if not normalized:
        raise ValueError("Task title is required.")
    duplicate = query("SELECT id FROM tasks WHERE user_id=? AND normalized_title=? AND id!=?",
                      (user_id, normalized, task_id or -1))
    if duplicate:
        raise ValueError("A task with the same title already exists. Edit the existing task instead.")
    fields = ("title","normalized_title","description","subject","category","scheduled_date",
              "start_time","end_time","deadline","priority","estimated_duration","status")
    vals = [title, normalized] + [data.get(k, "") for k in fields[2:]]
    if task_id:
        assignments = ",".join(f"{f}=?" for f in fields)
        execute(f"UPDATE tasks SET {assignments},updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?",
                vals + [task_id, user_id])
        return task_id
    return execute(f"INSERT INTO tasks(user_id,{','.join(fields)}) VALUES(?,{','.join(['?']*len(fields))})",
                   [user_id] + vals)

def delete_task(user_id, task_id):
    execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))

def set_task_status(user_id, task_id, status):
    execute("UPDATE tasks SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?",
            (status, task_id, user_id))

def list_logs(user_id):
    return query("SELECT * FROM study_logs WHERE user_id=? ORDER BY study_date DESC,id DESC", (user_id,))

def save_log(user_id, data, log_id=None):
    fields = ["study_date","subject","topic","planned_hours","actual_hours","tasks_assigned",
              "tasks_completed","sleep_hours","study_method","notes"]
    vals = [data.get(f) for f in fields]
    if log_id:
        execute("UPDATE study_logs SET " + ",".join(f"{f}=?" for f in fields) +
                " WHERE id=? AND user_id=?", vals + [log_id,user_id])
        return log_id
    return execute("INSERT INTO study_logs(user_id," + ",".join(fields) + ") VALUES(?" +
                   ",?"*len(fields) + ")", [user_id] + vals)

def delete_log(user_id, log_id):
    execute("DELETE FROM study_logs WHERE id=? AND user_id=?", (log_id,user_id))

def list_notes(user_id):
    return query("SELECT * FROM notes WHERE user_id=? ORDER BY pinned DESC,updated_at DESC", (user_id,))

def save_note(user_id, title, content, category="General", pinned=False, note_id=None):
    if note_id:
        execute("""UPDATE notes SET title=?,content=?,category=?,pinned=?,updated_at=CURRENT_TIMESTAMP
                   WHERE id=? AND user_id=?""", (title.strip(),content.strip(),category,int(pinned),note_id,user_id))
        return note_id
    return execute("""INSERT INTO notes(user_id,title,content,category,pinned)
                      VALUES(?,?,?,?,?)""", (user_id,title.strip(),content.strip(),category,int(pinned)))

def delete_note(user_id, note_id):
    execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id,user_id))

def list_plans(user_id):
    return query("SELECT * FROM plans WHERE user_id=? ORDER BY plan_date,start_time", (user_id,))

def clear_plans(user_id):
    execute("DELETE FROM plans WHERE user_id=?", (user_id,))

def add_plan(user_id, plan_date, subject, task_title, start_time, end_time, duration):
    execute("""INSERT INTO plans(user_id,plan_date,subject,task_title,start_time,end_time,duration)
               VALUES(?,?,?,?,?,?,?)""",
            (user_id,plan_date,subject,task_title,start_time,end_time,duration))

def update_settings(user_id, values):
    execute("""UPDATE users SET daily_limit=?,session_minutes=?,break_minutes=?,planning_days=?,theme=?
               WHERE id=?""", (*values, user_id))
