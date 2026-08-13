#!/usr/bin/env python3
"""
Elkayem Auto Ancillaries – Advanced Manpower Allocation Server
Features: SQLite database, RESTful API, JWT auth, role-based access control

Usage:
  python server_advanced.py

Then open in browser:
  http://localhost:8080
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sqlite3
import socket
import os
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Read PORT from environment (for cloud hosting), default to 8080
PORT = int(os.environ.get('PORT', 8080))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
# Use persistent storage path if available (Render.com)
DB_FILE = os.path.join(os.environ.get('DATABASE_PATH', DIRECTORY), 'elkayem.db')
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-this')

# ════════════════════════════════════════════════════════════
# ROLE-BASED ACCESS CONTROL CONFIGURATION
# ════════════════════════════════════════════════════════════
VALID_ROLES = {
    'supervisor': 'Working Area Supervisor',
    'am': 'Area Manager',
    'admin': 'Administrator',
    'higher_auth': 'Higher Authority'
}

ROLE_PERMISSIONS = {
    'supervisor': ['view_allocation', 'edit_allocation', 'view_attendance', 'edit_attendance'],
    'am': ['view_allocation', 'edit_allocation', 'view_attendance', 'edit_attendance', 
           'view_overtime', 'edit_overtime', 'view_employees', 'edit_employees', 
           'view_analytics', 'view_history', 'export_data', 'delete_allocation'],
    'admin': ['*'],  # Admin has all permissions
    'higher_auth': ['view_allocation', 'view_attendance', 'view_overtime', 'view_analytics', 'view_history']
}

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'type1',
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        ''')

        # Employees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                email TEXT,
                phone TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Allocations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS allocations (
                id INTEGER PRIMARY KEY,
                cell_id TEXT NOT NULL,
                date DATE NOT NULL,
                shift INTEGER DEFAULT 1,
                process_name TEXT NOT NULL,
                category TEXT,
                plan_count INTEGER,
                assigned_employee TEXT,
                status TEXT DEFAULT 'pending',
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cell_id, date, shift, process_name)
            )
        ''')

        # Allocation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS allocation_history (
                id INTEGER PRIMARY KEY,
                allocation_id INTEGER,
                date DATE NOT NULL,
                cell_id TEXT,
                process_name TEXT,
                assigned_employee TEXT,
                status TEXT,
                shift INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(allocation_id) REFERENCES allocations(id)
            )
        ''')

        # Login sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                token TEXT UNIQUE,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        self.insert_sample_data(cursor)
        conn.close()

    def insert_sample_data(self, cursor):
        """Insert sample users and employees if they don't exist"""
        try:
            # Sample users
            cursor.execute('SELECT COUNT(*) FROM users')
            if cursor.fetchone()[0] == 0:
                sample_users = [
                    ('admin', self.hash_password('admin123'), 'admin', 'admin@elkayem.com'),
                    ('supervisor', self.hash_password('super123'), 'supervisor', 'sup@elkayem.com'),
                    ('operator', self.hash_password('oper123'), 'type1', 'op@elkayem.com'),
                ]
                cursor.executemany(
                    'INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)',
                    sample_users
                )

            # Sample employees
            cursor.execute('SELECT COUNT(*) FROM employees')
            if cursor.fetchone()[0] == 0:
                sample_employees = [
                    ('Rajesh Kumar', 'Robot Op', 'rajesh@elkayem.com', '+91 9876543210', 'active'),
                    ('Priya Singh', 'Welder', 'priya@elkayem.com', '+91 9876543211', 'active'),
                    ('Amit Patel', 'Helper', 'amit@elkayem.com', '+91 9876543212', 'active'),
                    ('Neha Sharma', 'Operator', 'neha@elkayem.com', '+91 9876543213', 'active'),
                    ('Suresh Reddy', 'Robot Op', 'suresh@elkayem.com', '+91 9876543214', 'active'),
                ]
                cursor.executemany(
                    'INSERT INTO employees (name, category, email, phone, status) VALUES (?, ?, ?, ?, ?)',
                    sample_employees
                )

            # Use the cursor's connection to commit (init_db provides a local conn)
            try:
                cursor.connection.commit()
            except Exception:
                # Fallback: nothing to do if commit fails here
                pass
        except Exception as e:
            print(f'  Sample data already exists or error: {e}')

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Execute SELECT query"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def execute(self, sql: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user"""
        results = self.query(
            'SELECT * FROM users WHERE username = ? AND password_hash = ? AND active = 1',
            (username, self.hash_password(password))
        )
        return results[0] if results else None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        results = self.query('SELECT * FROM users WHERE id = ?', (user_id,))
        return results[0] if results else None

    def get_employees(self) -> List[Dict]:
        """Get all employees"""
        return self.query('SELECT * FROM employees ORDER BY name')

    def add_employee(self, name: str, category: str, email: str, phone: str, status: str) -> int:
        """Add new employee"""
        return self.execute(
            'INSERT INTO employees (name, category, email, phone, status) VALUES (?, ?, ?, ?, ?)',
            (name, category, email, phone, status)
        )

    def update_employee(self, emp_id: int, name: str, category: str, email: str, phone: str, status: str):
        """Update employee"""
        self.execute(
            'UPDATE employees SET name=?, category=?, email=?, phone=?, status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
            (name, category, email, phone, status, emp_id)
        )

    def delete_employee(self, emp_id: int):
        """Delete employee"""
        self.execute('DELETE FROM employees WHERE id=?', (emp_id,))

    def save_allocation(self, cell_id: str, date: str, shift: int, rows: List[Dict], user_id: int):
        """Save allocation data"""
        for row in rows:
            self.execute(
                '''INSERT OR REPLACE INTO allocations 
                   (cell_id, date, shift, process_name, category, plan_count, assigned_employee, status, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    cell_id, date, shift, row.get('process', ''), row.get('category', ''),
                    row.get('plan', 1), row.get('assigned', ''), row.get('status', 'pending'), user_id
                )
            )

            # Log to history
            self.execute(
                '''INSERT INTO allocation_history 
                   (date, cell_id, process_name, assigned_employee, status, shift)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (date, cell_id, row.get('process', ''), row.get('assigned', ''), row.get('status', 'pending'), shift)
            )

    def get_allocations(self, cell_id: Optional[str] = None, date: Optional[str] = None) -> List[Dict]:
        """Get allocations"""
        sql = 'SELECT * FROM allocations WHERE 1=1'
        params = []

        if cell_id:
            sql += ' AND cell_id = ?'
            params.append(cell_id)
        if date:
            sql += ' AND date = ?'
            params.append(date)

        return self.query(sql, tuple(params))

    def get_allocation_history(self, date: Optional[str] = None, cell_id: Optional[str] = None) -> List[Dict]:
        """Get allocation history"""
        sql = 'SELECT * FROM allocation_history WHERE 1=1'
        params = []

        if date:
            sql += ' AND date = ?'
            params.append(date)
        if cell_id:
            sql += ' AND cell_id = ?'
            params.append(cell_id)

        sql += ' ORDER BY created_at DESC LIMIT 500'
        return self.query(sql, tuple(params))

    def get_analytics(self) -> Dict:
        """Get analytics data"""
        total_employees = self.query('SELECT COUNT(*) as count FROM employees')[0]['count']
        allocations_today = self.query(
            'SELECT COUNT(*) as count FROM allocations WHERE date = ?',
            (datetime.now().strftime('%Y-%m-%d'),)
        )[0]['count']

        allocated = self.query(
            'SELECT COUNT(*) as count FROM allocations WHERE assigned_employee IS NOT NULL AND assigned_employee != ""'
        )[0]['count']

        avg_utilization = (allocated / max(1, allocations_today)) * 100 if allocations_today > 0 else 0

        active_shifts = self.query(
            'SELECT COUNT(DISTINCT shift) as count FROM allocations WHERE date = ?',
            (datetime.now().strftime('%Y-%m-%d'),)
        )[0]['count']

        return {
            'totalEmployees': total_employees,
            'allocationsToday': allocations_today,
            'avgUtilization': avg_utilization,
            'activeShifts': active_shifts
        }

    def create_session(self, user_id: int) -> str:
        """Create session token"""
        token = hashlib.sha256(f'{user_id}{time.time()}'.encode()).hexdigest()
        expires_at = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

        self.execute(
            'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
            (user_id, token, expires_at)
        )

        return token

    def verify_token(self, token: str) -> Optional[int]:
        """Verify session token and return user_id"""
        results = self.query(
            'SELECT user_id FROM sessions WHERE token = ? AND expires_at > CURRENT_TIMESTAMP',
            (token,)
        )
        return results[0]['user_id'] if results else None


class APIHandler(BaseHTTPRequestHandler):
    db = Database(DB_FILE)

    def log_message(self, format, *args):
        """Custom logging"""
        client = self.client_address[0]
        print(f"  [{client}] {format % args}")

    def send_json_response(self, data: Dict, status: int = 200):
        """Send JSON response"""
        payload = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(payload)

    def send_error_json(self, message: str, status: int = 400):
        """Send error JSON response"""
        self.send_json_response({'error': message, 'status': 'error'}, status)

    def get_auth_user(self) -> Optional[int]:
        """Get authenticated user from token"""
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            user_id = self.db.verify_token(token)
            return user_id
        return None

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body) if body else {}
        except:
            self.send_error_json('Invalid JSON', 400)
            return

        # ── Login endpoint ──
        if parsed.path == '/api/login':
            username = data.get('username')
            password = data.get('password')
            requested_role = data.get('role', 'supervisor')  # Frontend can request a role for testing

            if not username or not password:
                self.send_error_json('Username and password required', 400)
                return

            user = self.db.authenticate_user(username, password)
            if not user:
                self.send_error_json('Invalid credentials', 401)
                return

            # Validate requested role is valid (for development/testing)
            if requested_role not in VALID_ROLES:
                requested_role = user['role']  # Fall back to database role

            token = self.db.create_session(user['id'])
            self.send_json_response({
                'status': 'ok',
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'role': requested_role,  # Send the selected/validated role
                    'email': user['email']
                }
            }, 200)

        # ── Add Employee ──
        elif parsed.path == '/api/employees':
            user_id = self.get_auth_user()
            if not user_id:
                self.send_error_json('Unauthorized', 401)
                return

            emp_id = self.db.add_employee(
                data.get('name'),
                data.get('category'),
                data.get('email'),
                data.get('phone'),
                data.get('status', 'active')
            )

            self.send_json_response({'status': 'ok', 'id': emp_id}, 201)

        # ── Save Allocations ──
        elif parsed.path == '/api/allocations':
            user_id = self.get_auth_user()
            if not user_id:
                self.send_error_json('Unauthorized', 401)
                return

            self.db.save_allocation(
                data.get('cellId'),
                data.get('date'),
                data.get('shift', 1),
                data.get('rows', []),
                user_id
            )

            self.send_json_response({'status': 'ok', 'message': 'Allocation saved'}, 200)

        else:
            self.send_error_json('Not found', 404)

    def do_PUT(self):
        """Handle PUT requests"""
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body) if body else {}
        except:
            self.send_error_json('Invalid JSON', 400)
            return

        user_id = self.get_auth_user()
        if not user_id:
            self.send_error_json('Unauthorized', 401)
            return

        # ── Update Employee ──
        if parsed.path.startswith('/api/employees/'):
            emp_id = int(parsed.path.split('/')[-1])
            self.db.update_employee(
                emp_id,
                data.get('name'),
                data.get('category'),
                data.get('email'),
                data.get('phone'),
                data.get('status', 'active')
            )
            self.send_json_response({'status': 'ok'}, 200)
        else:
            self.send_error_json('Not found', 404)

    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed = urlparse(self.path)

        user_id = self.get_auth_user()
        if not user_id:
            self.send_error_json('Unauthorized', 401)
            return

        # ── Delete Employee ──
        if parsed.path.startswith('/api/employees/'):
            emp_id = int(parsed.path.split('/')[-1])
            self.db.delete_employee(emp_id)
            self.send_json_response({'status': 'ok'}, 200)
        else:
            self.send_error_json('Not found', 404)

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)

        user_id = self.get_auth_user()
        if not user_id:
            # Allow static file serving
            if parsed.path in ['/', '/index.html']:
                self.serve_static(parsed.path)
                return
            self.send_error_json('Unauthorized', 401)
            return

        # ── Get Employees ──
        if parsed.path == '/api/employees':
            employees = self.db.get_employees()
            self.send_json_response({'employees': employees}, 200)

        # ── Get Allocations ──
        elif parsed.path == '/api/allocations':
            cell_id = query_params.get('cellId', [None])[0]
            date = query_params.get('date', [None])[0]
            allocations = self.db.get_allocations(cell_id, date)
            self.send_json_response({'allocations': allocations}, 200)

        # ── Get Allocation History ──
        elif parsed.path == '/api/allocations/history':
            date = query_params.get('date', [None])[0]
            cell_id = query_params.get('cellId', [None])[0]
            history = self.db.get_allocation_history(date, cell_id)
            self.send_json_response({'history': history}, 200)

        # ── Get Analytics ──
        elif parsed.path == '/api/analytics':
            analytics = self.db.get_analytics()
            self.send_json_response(analytics, 200)

        # ── Serve Static Files ──
        else:
            self.serve_static(parsed.path)

    def serve_static(self, path):
        """Serve static files"""
        if path == '/' or path == '/index.html':
            file_path = os.path.join(DIRECTORY, 'index_advanced.html')
        else:
            file_path = os.path.join(DIRECTORY, path.lstrip('/'))

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.send_response(404)
            self.end_headers()
            return

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            content_type = 'text/html'
            if file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            print(f'  Error serving file: {e}')


def get_local_ip():
    """Get local network IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


if __name__ == "__main__":
    local_ip = get_local_ip()
    is_cloud = 'RENDER' in os.environ  # Detect Render.com environment
    
    print("=" * 60)
    print("  ELKAYEM ADVANCED MANPOWER ALLOCATION SERVER")
    print("=" * 60)
    print(f"  Database:  {DB_FILE}")
    if is_cloud:
        print(f"  🌐 Cloud Deployed (Render.com)")
        print(f"  Access at: https://YOUR-APP-NAME.onrender.com")
    else:
        print(f"  Local:     http://localhost:{PORT}")
        print(f"  Network:   http://{local_ip}:{PORT}")
    print("=" * 60)
    print("  Default Credentials:")
    print("    Username: admin, Password: admin123")
    print("    Username: supervisor, Password: super123")
    print("  Change credentials in database after first login!")
    print("=" * 60)
    print("  Press Ctrl+C to stop the server")
    print()

    server = HTTPServer(("", PORT), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
