a#!/usr/bin/env python3
"""
Elkayem Auto Ancillaries – Manpower Allocation Server v4
Supports: Allocation, Attendance, OT, Gas Flow, Targets, Leave, Skills, Reports, AI features
Usage: python3 server_v4.py
Open:  http://localhost:8080
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json, sqlite3, socket, os, hashlib, time
from datetime import datetime, timedelta

PORT     = 8080
DIR      = os.path.dirname(os.path.abspath(__file__))
DB_FILE  = os.path.join(DIR, 'elkayem_v4.db')

# ══════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════
class DB:
    def __init__(self, path):
        self.path = path
        self._init()

    def _init(self):
        c = self._conn()
        cur = c.cursor()

        cur.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'type1',
            email TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            token TEXT UNIQUE,
            expires_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            phone TEXT,
            skills TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY,
            cell_id TEXT NOT NULL,
            date TEXT NOT NULL,
            shift INTEGER DEFAULT 1,
            process_name TEXT NOT NULL,
            category TEXT,
            plan_count INTEGER DEFAULT 1,
            assigned_employee TEXT,
            remark TEXT,
            status TEXT DEFAULT 'pending',
            created_by INTEGER,
            approval_status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(cell_id, date, shift, process_name)
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            shift INTEGER DEFAULT 1,
            employee_name TEXT NOT NULL,
            process_name TEXT,
            cell TEXT,
            clock_in TEXT,
            clock_out TEXT,
            status TEXT DEFAULT 'Present',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, shift, employee_name)
        );
        CREATE TABLE IF NOT EXISTS ot_logs (
            id INTEGER PRIMARY KEY,
            employee_name TEXT NOT NULL,
            cell TEXT,
            date TEXT NOT NULL,
            hours REAL DEFAULT 0,
            reason TEXT,
            approved TEXT DEFAULT 'pending',
            month TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS gas_flow (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            shift_block TEXT NOT NULL,
            cell TEXT,
            model TEXT,
            process_name TEXT,
            mc_no TEXT,
            mc_name TEXT,
            actual_flow REAL,
            revised_flow REAL,
            reading_name TEXT,
            reason TEXT,
            supervisor TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, shift_block, cell, process_name, mc_no)
        );
        CREATE TABLE IF NOT EXISTS production_targets (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            shift INTEGER DEFAULT 1,
            cell INTEGER,
            product TEXT,
            target INTEGER DEFAULT 0,
            actual INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, shift, cell)
        );
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY,
            employee_name TEXT NOT NULL,
            leave_type TEXT,
            from_date TEXT,
            to_date TEXT,
            days INTEGER DEFAULT 1,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY,
            employee_name TEXT UNIQUE NOT NULL,
            skill_list TEXT,
            experience INTEGER DEFAULT 1,
            score INTEGER DEFAULT 7,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS allocation_history (
            id INTEGER PRIMARY KEY,
            date TEXT,
            cell TEXT,
            employee TEXT,
            process_name TEXT,
            shift TEXT,
            status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        c.commit()
        self._seed(cur, c)
        c.close()

    def _seed(self, cur, c):
        cur.execute('SELECT COUNT(*) FROM users')
        if cur.fetchone()[0] == 0:
            users = [
                ('admin',      self._hash('admin123'),  'admin',      'admin@elkayem.com'),
                ('supervisor', self._hash('super123'),  'supervisor', 'sup@elkayem.com'),
                ('operator',   self._hash('oper123'),   'type1',      'op@elkayem.com'),
            ]
            cur.executemany('INSERT INTO users (username,password_hash,role,email) VALUES (?,?,?,?)', users)

        cur.execute('SELECT COUNT(*) FROM employees')
        if cur.fetchone()[0] == 0:
            emps = [
                ('Rajesh Kumar',   'Robot Op', '+91 9876543210', 'Robot Op, MIG Welding', 'active'),
                ('Priya Singh',    'Welder',   '+91 9876543211', 'MIG Welding, TIG Welding', 'active'),
                ('Amit Patel',     'Helper',   '+91 9876543212', 'Material Handling, Cleaning', 'active'),
                ('Neha Sharma',    'Operator', '+91 9876543213', 'Boring, Revising, Inspection', 'active'),
                ('Suresh Reddy',   'Robot Op', '+91 9876543214', 'Robot Op, FANUC', 'active'),
                ('Meena Devi',     'Helper',   '+91 9876543215', 'Spatter Cleaning', 'active'),
                ('Karthik Raja',   'Welder',   '+91 9876543216', 'Full Welding, Rework', 'active'),
                ('Divya Lakshmi',  'Operator', '+91 9876543217', 'Gauge Inspection, Visual', 'active'),
            ]
            cur.executemany('INSERT INTO employees (name,category,phone,skills,status) VALUES (?,?,?,?,?)', emps)
        c.commit()

    @staticmethod
    def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

    def _conn(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def query(self, sql, params=()):
        c = self._conn()
        cur = c.cursor(); cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        c.close(); return rows

    def execute(self, sql, params=()):
        c = self._conn()
        cur = c.cursor(); cur.execute(sql, params)
        c.commit(); lid = cur.lastrowid; c.close(); return lid

    def executemany(self, sql, params_list):
        c = self._conn()
        cur = c.cursor(); cur.executemany(sql, params_list)
        c.commit(); c.close()

    def auth(self, username, password):
        r = self.query('SELECT * FROM users WHERE username=? AND password_hash=? AND active=1',
                       (username, self._hash(password)))
        return r[0] if r else None

    def create_session(self, user_id):
        token = hashlib.sha256(f'{user_id}{time.time()}'.encode()).hexdigest()
        exp   = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        self.execute('INSERT INTO sessions (user_id,token,expires_at) VALUES (?,?,?)',
                     (user_id, token, exp))
        return token

    def verify_token(self, token):
        r = self.query('SELECT user_id FROM sessions WHERE token=? AND expires_at>CURRENT_TIMESTAMP', (token,))
        return r[0]['user_id'] if r else None

    def get_user(self, uid):
        r = self.query('SELECT * FROM users WHERE id=?', (uid,))
        return r[0] if r else None


# ══════════════════════════════════════════════════════════════
# HTTP HANDLER
# ══════════════════════════════════════════════════════════════
class Handler(BaseHTTPRequestHandler):
    db = DB(DB_FILE)

    def log_message(self, fmt, *args):
        print(f'  [{self.client_address[0]}] {fmt % args}')

    # ── helpers ──
    def json_response(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        self.end_headers()
        self.wfile.write(body)

    def err(self, msg, status=400):
        self.json_response({'error': msg}, status)

    def read_body(self):
        n = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(n)
        try:    return json.loads(raw)
        except: return {}

    def auth_user(self):
        h = self.headers.get('Authorization', '')
        if h.startswith('Bearer '):
            uid = self.db.verify_token(h[7:])
            if uid: return self.db.get_user(uid)
        return None

    def serve_file(self, path):
        if not os.path.isfile(path):
            self.send_response(404); self.end_headers(); return
        ext = os.path.splitext(path)[1]
        ct  = {'html':'text/html','css':'text/css','js':'application/javascript','json':'application/json'}.get(ext.lstrip('.'), 'application/octet-stream')
        with open(path, 'rb') as f: body = f.read()
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── OPTIONS (CORS) ──
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        self.end_headers()

    # ══════════════════════════════════════════════════════════
    # GET
    # ══════════════════════════════════════════════════════════
    def do_GET(self):
        p = urlparse(self.path)
        path, qs = p.path, parse_qs(p.query)

        # Static files
        if path in ('/', '/index.html', '/elkayem_v4.html'):
            f = os.path.join(DIR, 'elkayem_v4.html')
            if not os.path.isfile(f): f = os.path.join(DIR, 'index_advanced.html')
            self.serve_file(f); return

        # API routes requiring auth
        user = self.auth_user()
        if not user and path.startswith('/api/') and path != '/api/login':
            self.err('Unauthorized', 401); return

        # ── Employees ──
        if path == '/api/employees':
            self.json_response({'employees': self.db.query('SELECT * FROM employees ORDER BY name')}); return

        # ── Allocations ──
        if path == '/api/allocations':
            cell = qs.get('cellId', [None])[0]
            date = qs.get('date',   [None])[0]
            sql  = 'SELECT * FROM allocations WHERE 1=1'
            par  = []
            if cell: sql += ' AND cell_id=?'; par.append(cell)
            if date: sql += ' AND date=?';    par.append(date)
            self.json_response({'allocations': self.db.query(sql, par)}); return

        # ── Allocation history ──
        if path == '/api/allocations/history':
            date = qs.get('date',   [None])[0]
            cell = qs.get('cellId', [None])[0]
            sql  = 'SELECT * FROM allocation_history WHERE 1=1'
            par  = []
            if date: sql += ' AND date=?';  par.append(date)
            if cell: sql += ' AND cell=?';  par.append('Cell '+cell)
            sql += ' ORDER BY created_at DESC LIMIT 500'
            self.json_response({'history': self.db.query(sql, par)}); return

        # ── Pending approvals (admin only) ──
        if path == '/api/allocations/pending':
            if user['role'] != 'admin': self.err('Forbidden', 403); return
            rows = self.db.query("SELECT * FROM allocations WHERE approval_status='pending' ORDER BY created_at DESC")
            self.json_response({'pending': rows}); return

        # ── Attendance ──
        if path == '/api/attendance':
            date  = qs.get('date',  [None])[0]
            shift = qs.get('shift', [None])[0]
            sql   = 'SELECT * FROM attendance WHERE 1=1'
            par   = []
            if date:  sql += ' AND date=?';  par.append(date)
            if shift: sql += ' AND shift=?'; par.append(shift)
            self.json_response({'attendance': self.db.query(sql, par)}); return

        # ── OT Logs ──
        if path == '/api/ot':
            month = qs.get('month', [None])[0]
            sql   = 'SELECT * FROM ot_logs WHERE 1=1'
            par   = []
            if month: sql += ' AND month=?'; par.append(month)
            sql += ' ORDER BY date DESC'
            self.json_response({'otLogs': self.db.query(sql, par)}); return

        # ── Gas Flow ──
        if path == '/api/gasflow':
            date = qs.get('date', [None])[0]
            sql  = 'SELECT * FROM gas_flow WHERE 1=1'
            par  = []
            if date: sql += ' AND date=?'; par.append(date)
            self.json_response({'rows': self.db.query(sql, par)}); return

        # ── Production Targets ──
        if path == '/api/targets':
            date  = qs.get('date',  [None])[0]
            shift = qs.get('shift', [None])[0]
            sql   = 'SELECT * FROM production_targets WHERE 1=1'
            par   = []
            if date:  sql += ' AND date=?';  par.append(date)
            if shift: sql += ' AND shift=?'; par.append(shift)
            self.json_response({'targets': self.db.query(sql, par)}); return

        # ── Leaves ──
        if path == '/api/leaves':
            month = qs.get('month', [None])[0]
            sql   = 'SELECT * FROM leaves WHERE 1=1'
            par   = []
            if month: sql += " AND strftime('%Y-%m', from_date)=?"; par.append(month)
            sql += ' ORDER BY created_at DESC'
            self.json_response({'leaves': self.db.query(sql, par)}); return

        # ── Skills ──
        if path == '/api/skills':
            self.json_response({'skills': self.db.query('SELECT * FROM skills ORDER BY employee_name')}); return

        # ── Analytics ──
        if path == '/api/analytics':
            today = datetime.now().strftime('%Y-%m-%d')
            month = datetime.now().strftime('%Y-%m')
            emp_count   = self.db.query('SELECT COUNT(*) as c FROM employees')[0]['c']
            alloc_today = self.db.query('SELECT COUNT(*) as c FROM allocations WHERE date=?', (today,))[0]['c']
            filled      = self.db.query("SELECT COUNT(*) as c FROM allocations WHERE date=? AND assigned_employee IS NOT NULL AND assigned_employee!=''", (today,))[0]['c']
            ot_hours    = self.db.query("SELECT COALESCE(SUM(hours),0) as h FROM ot_logs WHERE month=?", (month,))[0]['h']
            absent      = self.db.query("SELECT COUNT(*) as c FROM attendance WHERE date=? AND status='Absent'", (today,))[0]['c']
            on_leave    = self.db.query("SELECT COUNT(*) as c FROM leaves WHERE status='Approved' AND from_date<=? AND to_date>=?", (today, today))[0]['c']
            util        = round(filled / alloc_today * 100, 1) if alloc_today > 0 else 0
            self.json_response({
                'totalEmployees': emp_count, 'allocationsToday': alloc_today,
                'avgUtilization': util, 'otHours': float(ot_hours),
                'absentToday': absent, 'onLeave': on_leave
            }); return

        # ── Monthly Report ──
        if path == '/api/reports/monthly':
            month = qs.get('month', [datetime.now().strftime('%Y-%m')])[0]
            rows  = []
            for c in range(1, 12):
                total  = self.db.query("SELECT COUNT(*) as n FROM allocations WHERE cell_id=? AND strftime('%Y-%m',date)=?", (str(c), month))[0]['n']
                filled = self.db.query("SELECT COUNT(*) as n FROM allocations WHERE cell_id=? AND strftime('%Y-%m',date)=? AND assigned_employee!=''", (str(c), month))[0]['n']
                absent = self.db.query("SELECT COUNT(*) as n FROM allocations WHERE cell_id=? AND strftime('%Y-%m',date)=? AND remark='Absent'", (str(c), month))[0]['n']
                ot     = self.db.query("SELECT COALESCE(SUM(hours),0) as h FROM ot_logs WHERE cell=? AND month=?", (str(c), month))[0]['h']
                util   = round(filled / total * 100, 1) if total > 0 else 0
                rows.append({'cell': c, 'total': total, 'filled': filled, 'absent': absent, 'otHours': float(ot), 'util': util})
            self.json_response({'month': month, 'rows': rows}); return

        self.err('Not found', 404)

    # ══════════════════════════════════════════════════════════
    # POST
    # ══════════════════════════════════════════════════════════
    def do_POST(self):
        p    = urlparse(self.path).path
        data = self.read_body()

        # ── Login ──
        if p == '/api/login':
            u, pw = data.get('username'), data.get('password')
            if not u or not pw: self.err('Username and password required'); return
            user = self.db.auth(u, pw)
            if not user: self.err('Invalid credentials', 401); return
            token = self.db.create_session(user['id'])
            self.json_response({'status': 'ok', 'token': token, 'user': {
                'id': user['id'], 'username': user['username'],
                'role': user['role'], 'email': user['email']
            }}); return

        user = self.auth_user()
        if not user: self.err('Unauthorized', 401); return

        # ── Save Employee ──
        if p == '/api/employees':
            eid = self.db.execute(
                'INSERT INTO employees (name,category,phone,skills,status) VALUES (?,?,?,?,?)',
                (data.get('name'), data.get('category'), data.get('phone'),
                 data.get('skills'), data.get('status', 'active')))
            self.json_response({'id': eid}, 201); return

        # ── Save Allocation batch ──
        if p == '/api/allocations':
            cid   = data.get('cellId')
            date  = data.get('date')
            shift = data.get('shift', 1)
            rows  = data.get('rows', [])
            for r in rows:
                self.db.execute(
                    '''INSERT OR REPLACE INTO allocations
                       (cell_id,date,shift,process_name,category,plan_count,
                        assigned_employee,remark,status,created_by)
                       VALUES (?,?,?,?,?,?,?,?,?,?)''',
                    (cid, date, shift, r.get('process',''), r.get('category',''),
                     r.get('plan',1), r.get('assigned',''), r.get('remark',''),
                     r.get('status','pending'), user['id']))
                # history
                if r.get('assigned','').strip():
                    self.db.execute(
                        'INSERT INTO allocation_history (date,cell,employee,process_name,shift,status) VALUES (?,?,?,?,?,?)',
                        (date, 'Cell '+str(cid), r.get('assigned',''), r.get('process',''), 'Shift '+str(shift), r.get('status','pending')))
            self.json_response({'status': 'ok', 'saved': len(rows)}); return

        # ── Save Attendance ──
        if p == '/api/attendance':
            date  = data.get('date')
            shift = data.get('shift', 1)
            rows  = data.get('rows', [])
            for r in rows:
                self.db.execute(
                    '''INSERT OR REPLACE INTO attendance
                       (date,shift,employee_name,process_name,cell,clock_in,clock_out,status)
                       VALUES (?,?,?,?,?,?,?,?)''',
                    (date, shift, r.get('name',''), r.get('process',''),
                     r.get('cell',''), r.get('clockIn',''), r.get('clockOut',''), r.get('status','Present')))
            self.json_response({'status': 'ok'}); return

        # ── Save OT ──
        if p == '/api/ot':
            month = data.get('month')
            rows  = data.get('rows', [])
            # clear existing for this month first
            self.db.execute('DELETE FROM ot_logs WHERE month=?', (month,))
            for r in rows:
                self.db.execute(
                    'INSERT INTO ot_logs (employee_name,cell,date,hours,reason,approved,month) VALUES (?,?,?,?,?,?,?)',
                    (r.get('name',''), r.get('cell',''), r.get('date',''),
                     r.get('hours',0), r.get('reason',''), r.get('approved','pending'), month))
            self.json_response({'status': 'ok'}); return

        # ── Save Gas Flow ──
        if p == '/api/gasflow':
            date       = data.get('date')
            shift_block = data.get('shiftBlock')
            rows       = data.get('rows', [])
            for r in rows:
                self.db.execute(
                    '''INSERT OR REPLACE INTO gas_flow
                       (date,shift_block,cell,model,process_name,mc_no,mc_name,
                        actual_flow,revised_flow,reading_name,reason,supervisor)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (date, shift_block, r.get('cell'), r.get('model'), r.get('process'),
                     r.get('mcNo',''), r.get('mcName',''), r.get('actualFlow'),
                     r.get('revisedFlow'), r.get('name',''), r.get('reason',''), r.get('supervisor','')))
            self.json_response({'status': 'ok'}); return

        # ── Save Targets ──
        if p == '/api/targets':
            date  = data.get('date')
            shift = data.get('shift', 1)
            rows  = data.get('rows', [])
            for r in rows:
                self.db.execute(
                    '''INSERT OR REPLACE INTO production_targets
                       (date,shift,cell,product,target,actual)
                       VALUES (?,?,?,?,?,?)''',
                    (date, shift, r.get('cell'), r.get('product',''),
                     r.get('target',0), r.get('actual',0)))
            self.json_response({'status': 'ok'}); return

        # ── Apply Leave ──
        if p == '/api/leaves':
            lid = self.db.execute(
                'INSERT INTO leaves (employee_name,leave_type,from_date,to_date,days,reason,status) VALUES (?,?,?,?,?,?,?)',
                (data.get('emp',''), data.get('type','Casual'),
                 data.get('from'), data.get('to'), data.get('days',1),
                 data.get('reason',''), data.get('status','Pending')))
            self.json_response({'id': lid}, 201); return

        # ── Save Skills ──
        if p == '/api/skills':
            self.db.execute(
                '''INSERT OR REPLACE INTO skills
                   (employee_name,skill_list,experience,score,updated_at)
                   VALUES (?,?,?,?,CURRENT_TIMESTAMP)''',
                (data.get('employeeName'), data.get('skills',''),
                 data.get('exp',1), data.get('score',7)))
            self.json_response({'status': 'ok'}); return

        self.err('Not found', 404)

    # ══════════════════════════════════════════════════════════
    # PUT
    # ══════════════════════════════════════════════════════════
    def do_PUT(self):
        p    = urlparse(self.path).path
        data = self.read_body()
        user = self.auth_user()
        if not user: self.err('Unauthorized', 401); return

        # ── Update Employee ──
        if p.startswith('/api/employees/'):
            eid = p.split('/')[-1]
            self.db.execute(
                'UPDATE employees SET name=?,category=?,phone=?,skills=?,status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',
                (data.get('name'), data.get('category'), data.get('phone'),
                 data.get('skills',''), data.get('status','active'), eid))
            self.json_response({'status': 'ok'}); return

        # ── Approve Allocation ──
        if p.startswith('/api/allocations/approve/'):
            if user['role'] != 'admin': self.err('Forbidden', 403); return
            aid = p.split('/')[-1]
            self.db.execute("UPDATE allocations SET approval_status='approved' WHERE id=?", (aid,))
            self.json_response({'status': 'ok'}); return

        # ── Reject Allocation ──
        if p.startswith('/api/allocations/reject/'):
            if user['role'] != 'admin': self.err('Forbidden', 403); return
            aid = p.split('/')[-1]
            self.db.execute("UPDATE allocations SET approval_status='rejected' WHERE id=?", (aid,))
            self.json_response({'status': 'ok'}); return

        # ── Update Leave Status ──
        if p.startswith('/api/leaves/'):
            lid    = p.split('/')[-2] if p.endswith('/approve') or p.endswith('/reject') else p.split('/')[-1]
            status = 'Approved' if p.endswith('/approve') else 'Rejected' if p.endswith('/reject') else data.get('status','Pending')
            self.db.execute('UPDATE leaves SET status=? WHERE id=?', (status, lid))
            self.json_response({'status': 'ok'}); return

        self.err('Not found', 404)

    # ══════════════════════════════════════════════════════════
    # DELETE
    # ══════════════════════════════════════════════════════════
    def do_DELETE(self):
        p    = urlparse(self.path).path
        user = self.auth_user()
        if not user: self.err('Unauthorized', 401); return

        if p.startswith('/api/employees/'):
            eid = p.split('/')[-1]
            self.db.execute('DELETE FROM employees WHERE id=?', (eid,))
            self.json_response({'status': 'ok'}); return

        if p.startswith('/api/leaves/'):
            lid = p.split('/')[-1]
            self.db.execute('DELETE FROM leaves WHERE id=?', (lid,))
            self.json_response({'status': 'ok'}); return

        self.err('Not found', 404)


# ══════════════════════════════════════════════════════════════
# STARTUP
# ══════════════════════════════════════════════════════════════
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80)); ip = s.getsockname()[0]; s.close(); return ip
    except: return '127.0.0.1'

if __name__ == '__main__':
    ip = get_ip()
    print('=' * 60)
    print('  ELKAYEM MANPOWER ALLOCATION SERVER v4')
    print('=' * 60)
    print(f'  Database : {DB_FILE}')
    print(f'  Local    : http://localhost:{PORT}')
    print(f'  Network  : http://{ip}:{PORT}')
    print('=' * 60)
    print('  Default Logins:')
    print('    admin      / admin123  (full access)')
    print('    supervisor / super123  (manage allocations)')
    print('    operator   / oper123   (view only)')
    print('=' * 60)
    print('  API Endpoints:')
    print('    POST /api/login')
    print('    GET/POST /api/employees')
    print('    GET/POST /api/allocations')
    print('    GET/POST /api/attendance')
    print('    GET/POST /api/ot')
    print('    GET/POST /api/gasflow')
    print('    GET/POST /api/targets')
    print('    GET/POST /api/leaves')
    print('    GET/POST /api/skills')
    print('    GET      /api/analytics')
    print('    GET      /api/reports/monthly')
    print('=' * 60)
    print('  Press Ctrl+C to stop')
    print()

    server = HTTPServer(('', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Server stopped.')
