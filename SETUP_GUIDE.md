# Elkayem Auto Ancillaries – Advanced Manpower Allocation System

## 🚀 Quick Start

### Installation

1. **Place both files in the same directory:**
   ```
   your-project-folder/
   ├── server_advanced.py
   └── index_advanced.html
   ```

2. **Start the server:**
   ```bash
   python3 server_advanced.py
   ```

3. **Open in browser:**
   ```
   http://localhost:8080
   ```

4. **Default Login Credentials:**
   - **Username:** `admin`
   - **Password:** `admin123`

   Or try:
   - Username: `supervisor` / Password: `super123`
   - Username: `operator` / Password: `oper123`

---

## ✨ Key Features

### 1. **Dashboard & Analytics**
   - Real-time allocation statistics
   - Utilization percentage tracking
   - Total employees and shifts monitoring
   - Daily allocation overview

### 2. **Manpower Allocation**
   - Select cell/line and date
   - Assign employees to processes
   - Track allocation status (Pending → Assigned → Completed)
   - Real-time synchronization with backend
   - Support for multiple shifts (Shift 1, 2, 3)

### 3. **Employee Management**
   - Add/Edit/Delete employees
   - Categorize: Robot Operator, Welder, Helper, Operator
   - Track employee status (Active, Inactive, On Leave)
   - Store contact information (Email, Phone)
   - Searchable employee database

### 4. **Allocation History**
   - Track all allocation changes
   - Filter by date and cell
   - View historical assignments
   - Audit trail for compliance

### 5. **Export Functions**
   - **Export to Excel:** XLSX format with formatting
   - **Export to PDF:** Landscape layout for reports
   - Download allocations with full details

### 6. **Real-time Sync**
   - Sync button to refresh all data
   - localStorage caching for offline access
   - Automatic session management
   - Data persistence across sessions

### 7. **Role-Based Access Control**
   - Admin: Full access to all features
   - Supervisor: Can manage allocations and employees
   - Operator (Type 1): Limited allocation view only
   - User authentication with session tokens

### 8. **Advanced Search & Filtering**
   - Global search across employees and processes
   - Filter by cell, date, shift
   - Filter allocation history
   - Quick access to frequently used cells

---

## 📊 Architecture Overview

### Frontend (HTML5/JavaScript)
- **Modern UI:** Responsive sidebar navigation
- **Tab-based interface:** Allocation, Employees, Analytics, History, Settings
- **Real-time updates:** AJAX API calls
- **Local caching:** localStorage for offline access
- **Client-side validation:** Input error handling

### Backend (Python)
- **Database:** SQLite3 with proper schema
- **RESTful API:** Standard HTTP methods (GET, POST, PUT, DELETE)
- **Authentication:** Session-based tokens
- **Data validation:** Server-side checking
- **Audit logging:** Allocation history tracking

### Database Schema
```
Users Table:
  - id, username, password_hash, role, email, active

Employees Table:
  - id, name, category, email, phone, status, timestamps

Allocations Table:
  - id, cell_id, date, shift, process_name, category, plan_count, 
    assigned_employee, status, user_id, timestamps

Allocation History Table:
  - id, date, cell_id, process, assigned_employee, status, shift

Sessions Table:
  - id, user_id, token, expires_at, timestamps
```

---

## 🔌 API Endpoints

### Authentication
```
POST /api/login
  Request: { "username": "admin", "password": "admin123" }
  Response: { "token": "...", "user": { ... } }
```

### Employees
```
GET /api/employees
  Get all employees

POST /api/employees
  Create new employee
  Body: { "name": "...", "category": "...", "email": "...", "phone": "...", "status": "..." }

PUT /api/employees/{id}
  Update employee

DELETE /api/employees/{id}
  Delete employee
```

### Allocations
```
GET /api/allocations?cellId=1&date=2024-01-15
  Get allocations

POST /api/allocations
  Save allocation batch
  Body: { "cellId": "1", "date": "...", "shift": 1, "rows": [...] }

GET /api/allocations/history?date=2024-01-15&cellId=1
  Get allocation history
```

### Analytics
```
GET /api/analytics
  Response: { "totalEmployees": 0, "allocationsToday": 0, "avgUtilization": 0, "activeShifts": 0 }
```

---

## 🎨 Customization

### Change Company Details
1. Go to **Settings** tab
2. Update:
   - Company Name
   - Default Shift
   - Theme (Dark/Light mode - ready for future use)
3. Click **Save Settings**

### Add New Cells/Lines
Edit the `CELLS` object in HTML (around line ~800):
```javascript
"12": {
  label: "Cell 12 – Your New Line",
  processes: [
    { process: "Process Name", category: "Robot Op", plan: 1 },
    // ... more processes
  ]
}
```

### Change JWT Secret (Important!)
In `server_advanced.py`, line ~33:
```python
JWT_SECRET = 'change-this-to-a-strong-secret-key'
```

### Modify Database
Access SQLite directly:
```bash
sqlite3 elkayem.db
sqlite> SELECT * FROM users;
sqlite> SELECT * FROM employees;
```

---

## 🔐 Security Best Practices

1. **Change Default Passwords:** After first login, update credentials
2. **Use HTTPS:** Deploy with SSL certificate in production
3. **Strong JWT Secret:** Change the secret key
4. **Regular Backups:** Backup `elkayem.db` regularly
5. **Access Control:** Restrict access to server IP
6. **Database Encryption:** Consider encrypting sensitive data

### Change User Password
Direct database update (admin only):
```python
import hashlib
password_hash = hashlib.sha256('newpassword'.encode()).hexdigest()
# Then update database
```

---

## 📱 Network Access

### Same Network Access
1. Find your server IP:
   ```bash
   python3 -c "import socket; s = socket.socket(); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0])"
   ```

2. Share URL with team:
   ```
   http://<server-ip>:8080
   ```

3. All PCs on same network can access:
   - Same office network ✅
   - WiFi network ✅
   - Company LAN ✅

---

## 🐛 Troubleshooting

### Port 8080 Already in Use
```bash
# Find process using port 8080
lsof -i :8080

# Kill process
kill -9 <PID>

# Or use different port - edit server_advanced.py:
PORT = 8081
```

### Database Locked
- Close all browser tabs
- Restart server
- Delete `elkayem.db` and restart (loses data!)

### Can't Connect from Another PC
- Check firewall settings
- Ensure both PCs on same network
- Use IP address, not localhost
- Check network connectivity: `ping <server-ip>`

### Login Not Working
- Clear browser cache (Ctrl+Shift+Delete)
- Check database exists: `ls elkayem.db`
- Verify credentials in database
- Check server logs for errors

---

## 📈 Performance Tips

1. **Regular Cleanup:** Archive old allocations monthly
2. **Database Maintenance:** 
   ```bash
   sqlite3 elkayem.db "VACUUM;"
   ```
3. **Increase History Limit:** Edit query limit in `server_advanced.py`
4. **Batch Operations:** Use bulk export for large datasets

---

## 🔄 Backup & Restore

### Backup Database
```bash
cp elkayem.db elkayem.db.backup.$(date +%Y%m%d)
```

### Restore Database
```bash
cp elkayem.db.backup.20240115 elkayem.db
# Restart server
```

### Export All Data to CSV
Via SQL:
```bash
sqlite3 elkayem.db ".mode csv" ".output allocations.csv" "SELECT * FROM allocations;"
```

---

## 📝 Sample Workflow

### Daily Allocation Process

1. **Login** with your credentials
2. **Go to Allocation tab**
3. **Select Cell** (e.g., Cell 1)
4. **Select Date** (Today's date)
5. **Select Shift** (e.g., Shift 1)
6. **Click Load** to view processes
7. **Assign employees** to each process
8. **Update status** (Assigned/Completed)
9. **Click Save** to store
10. **Export** to Excel/PDF if needed

### Employee Management

1. **Go to Employees tab**
2. **Click Add Employee**
3. **Fill in details:**
   - Name
   - Category (Robot Op/Welder/Helper/Operator)
   - Email
   - Phone
   - Status (Active/Inactive/On Leave)
4. **Click Save Employee**

### View Analytics

1. **Go to Analytics tab**
2. **View real-time stats:**
   - Total Employees
   - Allocations Today
   - Avg Utilization %
   - Active Shifts
3. Charts coming soon

---

## 🚀 Future Enhancements

- [ ] Real-time collaboration (multiple users)
- [ ] Mobile app integration
- [ ] Advanced charting & reporting
- [ ] Predictive analytics
- [ ] Automated scheduling
- [ ] Machine learning optimization
- [ ] Multi-language support
- [ ] SMS/Email notifications
- [ ] Biometric integration
- [ ] Production tracking

---

## 📞 Support

For issues or questions:
1. Check logs in terminal
2. Review browser console (F12)
3. Verify database integrity
4. Restart server
5. Clear browser cache

---

## 📄 License

Internal Use Only - Elkayem Auto Ancillaries Pvt Ltd

---

**Version:** 2.0 Advanced  
**Last Updated:** January 2025  
**Status:** Production Ready
