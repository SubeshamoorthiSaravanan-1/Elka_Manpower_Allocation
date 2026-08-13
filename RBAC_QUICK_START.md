# ⚡ RBAC Quick Start Guide

## 🔐 Login & Role Selection

### Step 1: Access the Application
```
http://localhost:8080
```

### Step 2: Login Form Appears
- **Username:** `admin` (or `supervisor`)
- **Password:** `admin123` (or `super123`)
- **Role:** Select from dropdown (NEW!)
  - Supervisor (Working Area)
  - Area Manager (AM)
  - Administrator
  - Higher Authority

### Step 3: Click Sign In
Your selected role determines what you can see and do!

---

## 👥 Quick Role Overview

| Role | Main Job | Can Edit | Can Delete | Can Export |
|------|----------|----------|-----------|-----------|
| **Supervisor** | Daily ops | ✅ Limited | ❌ | ❌ |
| **Area Manager** | Oversee areas | ✅ All | ✅ Some | ✅ |
| **Admin** | System control | ✅ All | ✅ All | ✅ |
| **Higher Auth** | View reports | ❌ None | ❌ | ❌ |

---

## 🎯 What Each Role Sees

### Supervisor's Dashboard
```
Sidebar: 
  - ✅ Allocation
  - ✅ Attendance
  - ❌ Overtime (hidden)
  - ❌ Employees (hidden)
  - ❌ Analytics (hidden)
  - ❌ History (hidden)
  - ❌ Settings (hidden)
```

### Area Manager's Dashboard
```
Sidebar:
  - ✅ Allocation
  - ✅ Attendance
  - ✅ Overtime
  - ✅ Employees
  - ✅ Analytics
  - ✅ History
  - ❌ Settings (hidden)
  - ❌ Audit Log (hidden)
```

### Admin's Dashboard (Full Access)
```
Sidebar:
  - ✅ ALL tabs visible
  - ✅ Settings tab visible
  - ✅ Audit Log in Settings
  - ✅ Export & Clear options
```

### Higher Authority's Dashboard (View Only)
```
Sidebar:
  - ✅ Allocation (read-only)
  - ✅ Attendance (read-only)
  - ✅ Overtime (read-only)
  - ✅ Analytics (read-only)
  - ✅ History (read-only)
  - ❌ Edit buttons hidden
  - ❌ Delete buttons hidden
```

---

## 🛡️ Permission Examples

### Try This as Different Roles:

**Supervisor Login:**
1. Login → Select "Supervisor"
2. Go to Allocation tab
3. Try to delete a row → ❌ "Access denied: Delete allocation row"
4. Try to add/edit → ✅ Works!

**Area Manager Login:**
1. Login → Select "Area Manager"
2. Go to Allocation tab
3. Delete button appears → ✅ "Delete row" works
4. Go to Employees → ✅ Can see employees
5. Try to export → ✅ Works!

**Admin Login:**
1. Login → Select "Administrator"
2. Go to Settings tab → ✅ Audit Log visible
3. Click "Refresh Log" → Shows all actions
4. Click "Export Log" → Downloads as Excel

**Higher Authority Login:**
1. Login → Select "Higher Authority"
2. All data visible but read-only
3. No edit/delete buttons
4. Can only view and analyze

---

## 📊 Audit Log (Admin Only)

### View Audit Log:
1. Login as Admin
2. Go to **Settings** tab
3. Scroll down → "Audit Log (Admin Only)" section
4. See all user actions with:
   - Timestamp
   - Username & Role
   - Action taken
   - Details

### Example Audit Log:
```
2024-08-13 14:35:22 | rajesh (Supervisor) | SAVE_ALLOCATION | Saved allocation for Cell 1
2024-08-13 14:36:15 | priya (Area Manager) | CREATE_EMPLOYEE | Created employee: John Doe
2024-08-13 14:37:45 | admin (Administrator) | DELETE_EMPLOYEE | Deleted employee: Old Employee
```

### Export Audit Log:
- Click "Export Log" button
- Downloads `Audit_Log_2024-08-13.xlsx`
- Contains all logged actions

---

## ✅ Common Tasks by Role

### Supervisor Tasks
```
✅ View own cell allocations
✅ Assign employees to processes
✅ Mark attendance present/absent/late
✅ Update remarks (OT, Leave, etc.)
✅ Clear names for reallocation

❌ Cannot:
  - Delete anything
  - Manage employees
  - Export data
  - See analytics
  - View other cells
```

### Area Manager Tasks
```
✅ Manage allocations for all cells
✅ Manage employee database
✅ View overtime logs
✅ Approve/manage overtime
✅ View analytics & reports
✅ Export allocation sheets
✅ Delete allocations & OT records
✅ View full history

❌ Cannot:
  - Access system settings
  - View audit log
  - Delete employees
```

### Admin Tasks
```
✅ EVERYTHING including:
  - View all audit logs
  - Access all settings
  - Export all data
  - Clear all data
  - Manage all users
  - Reset passwords
```

### Higher Authority Tasks
```
✅ View all data
✅ See analytics & reports
✅ View historical data
✅ Export reports (coming soon)

❌ Cannot:
  - Edit anything
  - Delete anything
  - Manage employees
  - Access settings
```

---

## 🔔 Access Denied Messages

When you can't do something:

```
"Access denied: Edit allocation"
"Access denied: Delete employee"
"Access denied: Save settings"
"Access denied: View audit log"
```

**What to do:**
1. Check your role
2. Ask an Admin to change your role
3. Refer to the permissions matrix below

---

## 📋 Complete Permissions Matrix

```
Permission              Supervisor  AM  Admin  Higher Auth
─────────────────────────────────────────────────────────
view_allocation           ✅        ✅   ✅      ✅
edit_allocation           ✅        ✅   ✅      ❌
delete_allocation         ❌        ✅   ✅      ❌
view_attendance           ✅        ✅   ✅      ✅
edit_attendance           ✅        ✅   ✅      ❌
delete_attendance         ❌        ❌   ✅      ❌
view_overtime             ❌        ✅   ✅      ✅
edit_overtime             ❌        ✅   ✅      ❌
view_employees            ❌        ✅   ✅      ❌
edit_employees            ❌        ✅   ✅      ❌
delete_employees          ❌        ❌   ✅      ❌
view_analytics            ❌        ✅   ✅      ✅
view_history              ❌        ✅   ✅      ✅
export_data               ❌        ✅   ✅      ❌
export_all_data           ❌        ❌   ✅      ❌
manage_users              ❌        ❌   ✅      ❌
manage_settings           ❌        ❌   ✅      ❌
view_audit_log            ❌        ❌   ✅      ❌
clear_data                ❌        ❌   ✅      ❌
```

---

## 🧪 Testing Different Roles

### Quick Test:

1. **Login as Supervisor**
   ```
   Username: admin
   Password: admin123
   Role: Supervisor (Working Area)
   ```
   ✅ See: Allocation, Attendance
   ❌ See: Overtime, Employees, Analytics, Settings

2. **Logout** → Click Logout button

3. **Login as Area Manager**
   ```
   Username: admin
   Password: admin123
   Role: Area Manager (AM)
   ```
   ✅ See: All tabs + more features
   ❌ See: Settings tab

4. **Logout** → Click Logout button

5. **Login as Admin**
   ```
   Username: admin
   Password: admin123
   Role: Administrator
   ```
   ✅ See: ALL tabs including Settings with Audit Log!

---

## 💡 Pro Tips

1. **Check Your Role:** Look at user display (top right)
   ```
   Shows: username (Role Name)
   Example: rajesh (Supervisor)
   ```

2. **Permission Denied?** Toast message shows why
   ```
   "Access denied: Delete allocation row"
   ```

3. **Admin Audit Trail:** Track all changes in Audit Log
   - See who did what and when
   - Export for compliance

4. **Offline Mode:** Works even if server is down
   - Uses selected role locally
   - Syncs when back online

---

## 🔑 Demo Credentials

For testing different roles, use:

```
Username: admin
Password: admin123

Then select role at login:
- Supervisor (Working Area)
- Area Manager (AM)
- Administrator
- Higher Authority
```

Or additional account:
```
Username: supervisor
Password: super123
→ Always logs in as Supervisor
```

---

## ❓ FAQs

**Q: My buttons are hidden, why?**
A: Your role doesn't have permission. Logout and login with a different role.

**Q: Can I change my role?**
A: Logout and login with a different role selection (in offline mode). In production, Admin must change roles.

**Q: What if I click a disabled button?**
A: Nothing happens. Permission is checked before any action.

**Q: Where do I see what everyone did?**
A: Audit Log (Admin only) in Settings tab.

**Q: Is my data safe?**
A: Yes! Each role has specific permissions. Audit log tracks everything.

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't see Employees tab | Login with Area Manager or Admin role |
| Can't delete employee | Need Admin role (Area Manager can't delete) |
| Can't export data | Need Area Manager or Admin role |
| Can't view Audit Log | Need Admin role |
| Can't see Settings | Need Admin role |
| Access denied message | Check your role and permissions |

---

**Need More Details?** → Read `RBAC_GUIDE.md`
**Technical Details?** → Read `RBAC_IMPLEMENTATION_SUMMARY.md`

---

🎉 **You're ready to use the RBAC system!**
