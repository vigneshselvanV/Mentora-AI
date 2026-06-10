import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'mentora_users.db'
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create all tables if they don't exist"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          TEXT PRIMARY KEY,
            email       TEXT UNIQUE NOT NULL,
            username    TEXT NOT NULL,
            password    TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            last_login  TEXT,
            is_active   INTEGER DEFAULT 1,
            plan        TEXT DEFAULT 'free'
        )
    ''')
    
    # Sessions table (for token blacklisting)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token_id    TEXT PRIMARY KEY,
            user_id     TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            expires_at  TEXT NOT NULL,
            is_valid    INTEGER DEFAULT 1
        )
    ''')
    
    # User progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id           TEXT PRIMARY KEY,
            total_questions   INTEGER DEFAULT 0,
            topics_explored   TEXT DEFAULT '{}',
            recent_activity   TEXT DEFAULT '[]',
            streak            INTEGER DEFAULT 0,
            last_active_date  TEXT,
            quiz_results      TEXT DEFAULT '[]',
            bookmarks         TEXT DEFAULT '[]',
            chat_sessions     TEXT DEFAULT '[]',
            saved_paths       TEXT DEFAULT '[]',
            difficulty        TEXT DEFAULT 'beginner',
            updated_at        TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized!")

def create_user(id, email, username,
                hashed_password):
    """Insert new user into database"""
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO users
            (id, email, username, password,
             created_at, plan)
            VALUES (?,?,?,?,?,?)
        ''', (id, email.lower().strip(),
              username, hashed_password,
              datetime.utcnow().isoformat(),
              'free'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE email=?',
        (email.lower().strip(),)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE id=?',
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def update_last_login(user_id):
    """Update last login timestamp"""
    conn = get_db()
    conn.execute(
        '''UPDATE users SET last_login=?
           WHERE id=?''',
        (datetime.utcnow().isoformat(), user_id)
    )
    conn.commit()
    conn.close()

def get_user_data(user_id):
    """Get user progress/data"""
    conn = get_db()
    data = conn.execute(
        'SELECT * FROM user_progress WHERE user_id=?',
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(data) if data else None

def save_user_data(user_id, data_dict):
    """Save or update user progress data"""
    import json
    conn = get_db()
    existing = conn.execute(
        'SELECT user_id FROM user_progress WHERE user_id=?',
        (user_id,)
    ).fetchone()
    
    if existing:
        conn.execute('''
            UPDATE user_progress SET
            total_questions=?,
            topics_explored=?,
            recent_activity=?,
            streak=?,
            last_active_date=?,
            quiz_results=?,
            bookmarks=?,
            chat_sessions=?,
            saved_paths=?,
            difficulty=?,
            updated_at=?
            WHERE user_id=?
        ''', (
            data_dict.get('totalQuestions', 0),
            json.dumps(
                data_dict.get('topicsExplored',{})),
            json.dumps(
                data_dict.get('recentActivity',[])),
            data_dict.get('streak', 0),
            data_dict.get('lastActiveDate'),
            json.dumps(
                data_dict.get('quizResults',[])),
            json.dumps(
                data_dict.get('bookmarks',[])),
            json.dumps(
                data_dict.get('sessions',[])),
            json.dumps(
                data_dict.get('savedPaths',[])),
            data_dict.get('difficulty','beginner'),
            datetime.utcnow().isoformat(),
            user_id
        ))
    else:
        conn.execute('''
            INSERT INTO user_progress
            (user_id, total_questions,
             topics_explored, recent_activity,
             streak, last_active_date,
             quiz_results, bookmarks,
             chat_sessions, saved_paths,
             difficulty, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            user_id,
            data_dict.get('totalQuestions', 0),
            json.dumps(
                data_dict.get('topicsExplored',{})),
            json.dumps(
                data_dict.get('recentActivity',[])),
            data_dict.get('streak', 0),
            data_dict.get('lastActiveDate'),
            json.dumps(
                data_dict.get('quizResults',[])),
            json.dumps(
                data_dict.get('bookmarks',[])),
            json.dumps(
                data_dict.get('sessions',[])),
            json.dumps(
                data_dict.get('savedPaths',[])),
            data_dict.get('difficulty','beginner'),
            datetime.utcnow().isoformat()
        ))
    
    conn.commit()
    conn.close()
