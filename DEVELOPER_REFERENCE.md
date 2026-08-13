# Elkayem Manpower System – Developer Reference

## 🔧 Quick Commands

### Start Server
```bash
python3 server_advanced.py
```

### Run in Background
```bash
nohup python3 server_advanced.py > server.log 2>&1 &
```

### Stop Server
```bash
pkill -f "server_advanced.py"
```

### Check if Running
```bash
ps aux | grep server_advanced
```

---

## 🗄️ Database Operations

### Connect to Database
```bash
sqlite3 elkayem.db
```

### View All Tables
```sql
.tables
```

### Table Schemas
```sql
.schema users
.schema employees
.schema allocations
.schema allocation_history
.schema sessions
```

### Export to CSV
```bash
sqlite3 elkayem.db ".mode csv" ".headers on" ".output allocations.csv" "SELECT * FROM allocations;"
```

### Export to JSON (requires jq)
```bash
sqlite3 elkayem.db ".mode json" "SELECT * FROM employees;" | jq . > employees.json
```

---

## 👥 User Management

### Add New User
```sql
INSERT INTO users (username, password_hash, role, email, active) 
VALUES ('newuser', '5e884898da28047151d0e56f8dc6292773603d0d7aae720be341abebc7d91a', 'type1', 'email@elkayem.com', 1);
```
*Password hash above is SHA256 of "password"*

### List All Users
```sql
SELECT id, username, role, email, active FROM users;
```

### Change User Role
```sql
UPDATE users SET role = 'supervisor' WHERE username = 'john';
```

### Deactivate User
```sql
UPDATE users SET active = 0 WHERE username = 'olduser';
```

### Reset Password
```sql
UPDATE users SET password_hash = '5e884898da28047151d0e56f8dc6292773603d0d7aae720be341abebc7d91a' WHERE username = 'admin';
```

### Delete User
```sql
DELETE FROM users WHERE username = 'olduser';
```

---

## 👨‍💼 Employee Management

### Add Employee
```sql
INSERT INTO employees (name, category, email, phone, status) 
VALUES ('Rajesh Kumar', 'Robot Op', 'rajesh@elkayem.com', '+91 9876543210', 'active');
```

### List All Employees
```sql
SELECT * FROM employees ORDER BY name;
```

### List by Category
```sql
SELECT * FROM employees WHERE category = 'Welder' AND status = 'active';
```

### Update Employee
```sql
UPDATE employees SET status = 'on leave' WHERE id = 5;
```

### Count Employees by Category
```sql
SELECT category, COUNT(*) as count FROM employees WHERE status = 'active' GROUP BY category;
```

### Search Employee
```sql
SELECT * FROM employees WHERE name LIKE '%kumar%' OR email LIKE '%kumar%';
```

### Bulk Import from CSV
```bash
# Create CSV: employees.csv with columns: name,category,email,phone,status
sqlite3 elkayem.db ".mode csv" ".import employees.csv temp_import"
```

---

## 📋 Allocation Operations

### View Today's Allocations
```sql
SELECT * FROM allocations 
WHERE date = DATE('now') 
ORDER BY cell_id, process_name;
```

### View Allocations by Cell
```sql
SELECT * FROM allocations 
WHERE cell_id = '1' AND date = '2024-01-15' 
ORDER BY process_name;
```

### View Unassigned Positions
```sql
SELECT cell_id, process_name, category, plan_count 
FROM allocations 
WHERE (assigned_employee IS NULL OR assigned_employee = '') 
AND date = DATE('now');
```

### Count Allocations by Status
```sql
SELECT status, COUNT(*) as count 
FROM allocations 
WHERE date = DATE('now') 
GROUP BY status;
```

### View by Shift
```sql
SELECT * FROM allocations 
WHERE date = DATE('now') AND shift = 1 
ORDER BY cell_id;
```

### Get Assigned Employees
```sql
SELECT DISTINCT assigned_employee FROM allocations 
WHERE assigned_employee IS NOT NULL AND assigned_employee != '' 
ORDER BY assigned_employee;
```

### Utilization Report
```sql
SELECT cell_id, 
  COUNT(*) as total_positions,
  SUM(CASE WHEN assigned_employee != '' THEN 1 ELSE 0 END) as assigned,
  ROUND(SUM(CASE WHEN assigned_employee != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as utilization_percent
FROM allocations 
WHERE date = DATE('now')
GROUP BY cell_id;
```

### Delete Old Allocations (before date)
```sql
DELETE FROM allocations WHERE date < '2024-01-01';
DELETE FROM allocation_history WHERE date < '2024-01-01';
```

---

## 📊 History & Audit

### View Allocation History
```sql
SELECT * FROM allocation_history 
WHERE date = DATE('now') 
ORDER BY created_at DESC;
```

### History by Employee
```sql
SELECT * FROM allocation_history 
WHERE assigned_employee = 'Rajesh Kumar' 
ORDER BY created_at DESC;
```

### Changes Made Today
```sql
SELECT * FROM allocation_history 
WHERE date = DATE('now') 
ORDER BY created_at DESC 
LIMIT 50;
```

### Audit Trail (who changed what when)
```sql
SELECT 
  ah.created_at,
  ah.assigned_employee,
  ah.process_name,
  ah.status,
  u.username as changed_by
FROM allocation_history ah
LEFT JOIN users u ON u.id = ah.user_id
ORDER BY ah.created_at DESC;
```

---

## 🔑 Session Management

### View Active Sessions
```sql
SELECT u.username, s.token, s.expires_at, s.created_at 
FROM sessions s 
JOIN users u ON u.id = s.user_id 
WHERE s.expires_at > CURRENT_TIMESTAMP;
```

### Expire All Sessions for User
```sql
UPDATE sessions SET expires_at = CURRENT_TIMESTAMP 
WHERE user_id = (SELECT id FROM users WHERE username = 'olduser');
```

### Clear Expired Sessions
```sql
DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP;
```

---

## 📈 Analytics Queries

### Daily Summary
```sql
SELECT 
  DATE('now') as date,
  COUNT(DISTINCT cell_id) as cells_active,
  COUNT(*) as total_positions,
  SUM(CASE WHEN assigned_employee != '' THEN 1 ELSE 0 END) as assigned_positions,
  COUNT(DISTINCT assigned_employee) as unique_employees,
  ROUND(SUM(CASE WHEN assigned_employee != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as utilization_pct
FROM allocations 
WHERE date = DATE('now');
```

### Weekly Report
```sql
SELECT 
  strftime('%Y-W%W', date) as week,
  COUNT(DISTINCT date) as days_worked,
  COUNT(*) as total_positions,
  SUM(CASE WHEN assigned_employee != '' THEN 1 ELSE 0 END) as assigned,
  COUNT(DISTINCT cell_id) as cells_active
FROM allocations 
GROUP BY strftime('%Y-W%W', date)
ORDER BY week DESC
LIMIT 4;
```

### Employee Utilization
```sql
SELECT 
  assigned_employee,
  COUNT(*) as allocations,
  COUNT(DISTINCT DATE(created_at)) as days_worked,
  COUNT(DISTINCT cell_id) as cells_assigned
FROM allocations 
WHERE assigned_employee != '' AND date >= DATE('now', '-30 days')
GROUP BY assigned_employee
ORDER BY allocations DESC;
```

### Process Analysis
```sql
SELECT 
  process_name,
  category,
  COUNT(*) as total_allocations,
  COUNT(DISTINCT assigned_employee) as unique_assignees,
  AVG(plan_count) as avg_plan
FROM allocations 
GROUP BY process_name
ORDER BY total_allocations DESC;
```

---

## 🔍 Advanced Debugging

### View Recent Errors (check server logs)
```bash
tail -n 50 server.log
```

### Database Integrity Check
```bash
sqlite3 elkayem.db "PRAGMA integrity_check;"
```

### Database Size
```bash
ls -lh elkayem.db
sqlite3 elkayem.db "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();"
```

### Optimize Database
```bash
sqlite3 elkayem.db "VACUUM; ANALYZE;"
```

### View Query Performance
```bash
sqlite3 elkayem.db ".timer on"
# Run queries and check execution time
```

---

## 🧪 Testing

### Create Test User
```sql
INSERT INTO users (username, password_hash, role, email) 
VALUES ('testuser', '5e884898da28047151d0e56f8dc6292773603d0d7aae720be341abebc7d91a', 'type1', 'test@elkayem.com');
```

### Populate Test Data
```bash
# Run this script to generate test data
python3 << 'EOF'
import sqlite3
from datetime import datetime, timedelta
import random

db = sqlite3.connect('elkayem.db')
c = db.cursor()

# Add test employees
for i in range(20):
    c.execute('''INSERT OR IGNORE INTO employees (name, category, email, phone, status) 
                 VALUES (?, ?, ?, ?, ?)''',
              (f'Test Employee {i+1}', random.choice(['Robot Op', 'Welder', 'Helper', 'Operator']),
               f'emp{i+1}@elkayem.com', f'900000000{i:02d}', 'active'))

# Add test allocations for past 7 days
for d in range(7):
    date = (datetime.now() - timedelta(days=d)).strftime('%Y-%m-%d')
    for cell in ['1', '2', '3']:
        for process_num in range(1, 4):
            c.execute('''INSERT OR IGNORE INTO allocations 
                        (cell_id, date, shift, process_name, category, plan_count, assigned_employee, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (cell, date, random.choice([1, 2, 3]), f'Process {process_num}',
                      random.choice(['Robot Op', 'Welder', 'Helper']), 1,
                      f'Test Employee {random.randint(1, 20)}', random.choice(['pending', 'assigned', 'completed'])))

db.commit()
db.close()
print("Test data created!")
EOF
```

### Clear Test Data
```bash
sqlite3 elkayem.db "DELETE FROM allocations; DELETE FROM allocation_history; DELETE FROM employees; VACUUM;"
```

---

## 🔗 API Testing

### Test Login
```bash
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Get Employees (requires token from login)
```bash
curl -X GET http://localhost:8080/api/employees \
  -H "Authorization: Bearer <TOKEN_HERE>"
```

### Get Analytics
```bash
curl -X GET http://localhost:8080/api/analytics \
  -H "Authorization: Bearer <TOKEN_HERE>"
```

### Create Allocation
```bash
curl -X POST http://localhost:8080/api/allocations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN_HERE>" \
  -d '{
    "cellId": "1",
    "date": "2024-01-15",
    "shift": 1,
    "rows": [
      {"process": "Welding", "category": "Welder", "plan": 1, "assigned": "Rajesh Kumar", "status": "assigned"}
    ]
  }'
```

---

## 📝 Common Tasks

### Backup Before Major Changes
```bash
cp elkayem.db elkayem.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Restore from Backup
```bash
cp elkayem.db.backup.20240115_143022 elkayem.db
# Restart server
```

### Generate Monthly Report
```bash
sqlite3 elkayem.db << EOF
.mode list
.separator "|"
.output monthly_report_2024_01.txt
SELECT * FROM allocations WHERE strftime('%Y-%m', date) = '2024-01' ORDER BY date, cell_id;
.quit
EOF
```

### Merge Databases (advanced)
```bash
sqlite3 elkayem.db "ATTACH 'other.db' AS other; INSERT INTO employees SELECT * FROM other.employees;"
```

---

## 🚨 Emergency Procedures

### Server Won't Start
1. Check if port is in use: `lsof -i :8080`
2. Check Python installation: `python3 --version`
3. Check file permissions: `ls -l server_advanced.py`
4. Check database: `sqlite3 elkayem.db ".tables"`

### Database Corruption
```bash
# Backup corrupted database
mv elkayem.db elkayem.db.corrupted

# Dump and restore
sqlite3 elkayem.db.corrupted ".dump" | sqlite3 elkayem.db
```

### Lost Admin Password
```sql
-- Reset to default
UPDATE users SET password_hash = '5e884898da28047151d0e56f8dc6292773603d0d7aae720be341abebc7d91a' WHERE username = 'admin';
-- Now login with password: 'password'
-- Change immediately after login!
```

### Database Locked
```bash
# Kill all connections and restart
pkill -f "server_advanced.py"
sleep 2
rm -f elkayem.db-*
python3 server_advanced.py
```

---

## 📚 Python Password Hash Utility

```python
#!/usr/bin/env python3
import hashlib
import sys

if len(sys.argv) < 2:
    print("Usage: python hash_password.py <password>")
    sys.exit(1)

password = sys.argv[1]
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(f"Password: {password}")
print(f"Hash: {hash_value}")
```

Usage:
```bash
python3 hash_password.py "mynewpassword"
# Copy hash and update database
```

---

**Last Updated:** January 2025  
**Version:** 2.0 Advanced
