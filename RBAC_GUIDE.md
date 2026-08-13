# 🔐 Role-Based Access Control (RBAC) Guide

## Overview
The Elkayem Manpower Allocation System now includes comprehensive role-based access control (RBAC) to restrict features and data access based on user roles.

---

## 📋 Roles & Permissions Matrix

### 1. **SUPERVISOR** (Working Area Supervisor)
**Purpose:** Manages day-to-day operations for their assigned cell/line

| Feature | Permission | Access |
|---------|-----------|--------|
| View Allocations | ✅ | Own cell/area only |
| Edit Allocations | ✅ | Assign employees, update status |
| View Attendance | ✅ | Mark attendance for assigned area |
| Edit Attendance | ✅ | Update attendance records |
| View Employees | ❌ | No access |
| Edit Employees | ❌ | Cannot manage employee database |
| View Analytics | ❌ | No access |
| View History | ❌ | No access |
| View Settings | ❌ | No access |
| Export Data | ❌ | No access |
| Delete Records | ❌ | Cannot delete |
| View Audit Log | ❌ | No access |

---

### 2. **AM** (Area Manager)
**Purpose:** Oversees multiple supervisors and cells; makes strategic decisions

| Feature | Permission | Access |
|---------|-----------|--------|
| View Allocations | ✅ | All cells |
| Edit Allocations | ✅ | Can modify any cell allocation |
| View Attendance | ✅ | All records |
| Edit Attendance | ✅ | Full access |
| View Employees | ✅ | Full employee database |
| Edit Employees | ✅ | Add/modify/view employees |
| View Overtime | ✅ | All OT logs |
| Edit Overtime | ✅ | Approve/manage OT |
| View Analytics | ✅ | Dashboard & reports |
| View History | ✅ | Full audit trail |
| Export Data | ✅ | Export allocation sheets |
| Delete Records | ✅ | Delete allocations only |
| View Audit Log | ❌ | No access |
| Clear Data | ❌ | Cannot clear all data |

---

### 3. **ADMIN** (Administrator)
**Purpose:** Full system control; maintenance and configuration

| Feature | Permission | Access |
|---------|-----------|--------|
| **ALL FEATURES** | ✅ | **FULL ACCESS** |
| Manage Users | ✅ | Create/modify user accounts |
| System Settings | ✅ | Configure application |
| View Audit Log | ✅ | See all user actions |
| Clear All Data | ✅ | Reset database |
| User Roles | ✅ | Assign roles to users |

---

### 4. **HIGHER AUTHORITY** (Director/Top Management)
**Purpose:** View-only access for strategic oversight

| Feature | Permission | Access |
|---------|-----------|--------|
| View Allocations | ✅ | All cells - READ ONLY |
| View Attendance | ✅ | READ ONLY |
| View Overtime | ✅ | READ ONLY |
| View Analytics | ✅ | Dashboard & reports |
| View History | ✅ | Full audit trail |
| Edit/Modify | ❌ | No editing permissions |
| Delete Records | ❌ | No deletion |
| Export Data | ❌ | No export access |

---

## 🔑 Login & Role Selection

### At Login Screen:
1. Enter **Username** and **Password**
2. Select **Role** from dropdown:
   - Supervisor (Working Area)
   - Area Manager (AM)
   - Administrator
   - Higher Authority

### Online Mode (Server Running):
- Server validates credentials against database
- Server may override selected role with database role for security
- Session token is issued

### Offline Mode (Server Down):
- Application works in local storage mode
- Selected role is honored locally
- No server validation

---

## 📊 UI Changes Based on Role

### Sidebar Navigation Tabs Visibility:

| Tab | Supervisor | AM | Admin | Higher Auth |
|-----|-----------|----|----|--------|
| Allocation | ✅ | ✅ | ✅ | ✅ |
| Attendance | ✅ | ✅ | ✅ | ✅ |
| Overtime | ❌ | ✅ | ✅ | ✅ |
| Employees | ❌ | ✅ | ✅ | ❌ |
| Analytics | ❌ | ✅ | ✅ | ✅ |
| History | ❌ | ✅ | ✅ | ✅ |
| Settings | ❌ | ❌ | ✅ | ❌ |

### Action Buttons Visibility:

| Action | Supervisor | AM | Admin | Higher Auth |
|--------|-----------|----|----|--------|
| Add/Edit Allocation | ✅ | ✅ | ✅ | ❌ |
| Delete Allocation | ❌ | ✅ | ✅ | ❌ |
| Add/Edit Employee | ❌ | ✅ | ✅ | ❌ |
| Delete Employee | ❌ | ❌ | ✅ | ❌ |
| Export Sheet | ❌ | ✅ | ✅ | ❌ |
| View Audit Log | ❌ | ❌ | ✅ | ❌ |

---

## 🛡️ Permission Checking

### How It Works:

1. **Frontend Check (UI Level)**
   ```javascript
   if(hasPermission('edit_allocation')) {
     // Show edit buttons
   }
   ```

2. **Before Action Execution**
   ```javascript
   if(!canPerform('save_allocation', 'Save Allocation')) return;
   // Proceed with save
   ```

3. **Audit Logging**
   ```javascript
   logAudit('SAVE_ALLOCATION', 'Saved allocation for Cell 1...');
   ```

---

## 📝 Audit Logging

### What Gets Logged:
- ✅ User login/logout
- ✅ Data saves (allocations, employees, attendance)
- ✅ Data deletions
- ✅ Exports & backups
- ✅ Settings changes
- ✅ Access attempts (including denied)

### Access Audit Log:
- **Admin Only** can view the full audit log
- Located in **Settings** tab
- Shows: Timestamp | User | Role | Action | Details
- Can be exported as Excel

### Audit Log Example:
```
2024-08-13 14:35:22 | rajesh | Supervisor | SAVE_ALLOCATION | Saved allocation for Cell 1 on 2024-08-13 Shift 1 (21 entries)
2024-08-13 14:36:15 | priya  | Area Manager | CREATE_EMPLOYEE | Created employee: John Doe
2024-08-13 14:37:45 | admin  | Administrator | DELETE_EMPLOYEE | Deleted employee: Old Employee
```

---

## 🔔 Denied Access Messages

When a user tries to access a feature they don't have permission for:

```
"Access denied: Edit allocation"
"Access denied: Delete employee"
"Access denied: View audit log"
```

---

## 🚀 Using Different Roles

### For Testing Different Roles:

1. **Log out** (use Logout button)
2. **At login screen**, select different role and use credentials:
   - Username: `admin` / Password: `admin123`
   - Username: `supervisor` / Password: `super123`
   
3. Each role will see different UI and have different capabilities

### Test Scenario:

**Supervisor Login:**
- Can see Allocation & Attendance tabs only
- Cannot delete or export data
- All delete buttons hidden

**Area Manager Login:**
- Can see Allocation, Attendance, Overtime, Employees, Analytics, History
- Can delete allocations and manage employees
- Can export data
- Cannot access Settings or Audit Log

**Admin Login:**
- Full access to all features
- Settings tab visible with System Settings
- Audit Log visible at bottom of Settings

---

## 🔧 Backend Implementation

### Server Role Validation:
Located in `server_advanced.py`:

```python
VALID_ROLES = {
    'supervisor': 'Working Area Supervisor',
    'am': 'Area Manager',
    'admin': 'Administrator',
    'higher_auth': 'Higher Authority'
}

ROLE_PERMISSIONS = {
    'supervisor': ['view_allocation', 'edit_allocation', ...],
    'am': [...permissions...],
    'admin': ['*'],  # All permissions
    'higher_auth': [...limited...]
}
```

---

## 💾 Audit Log Storage

### Storage Location:
- **Browser LocalStorage** key: `auditLog`
- **Format:** JSON array
- **Limit:** Last 1000 entries (auto-pruning)

### Export Audit Log:
- Admin can export audit log as Excel
- Filename: `Audit_Log_YYYY-MM-DD.xlsx`
- Contains all logged actions

---

## 🔐 Security Best Practices

1. ✅ **Change Default Passwords:**
   ```
   Default credentials in server:
   - admin / admin123
   - supervisor / super123
   CHANGE THESE IMMEDIATELY
   ```

2. ✅ **JWT Secret Key:**
   Update in `server_advanced.py`:
   ```python
   JWT_SECRET = 'your-strong-secret-key-here'
   ```

3. ✅ **Regular Audit Log Review:**
   - Admin should review audit logs regularly
   - Look for suspicious activities
   - Track data modifications

4. ✅ **Role Assignment:**
   - Never give admin role to operators
   - Supervisor role limited to area supervisors
   - Higher Authority for view-only access

---

## ❓ FAQ

**Q: Can I change my role?**
A: Logout and login with a different role selection. In production, only Admin can change roles via user management.

**Q: What if I try to edit something I don't have permission for?**
A: You'll see an access denied message and no changes will be made.

**Q: Can Supervisor see other employees' allocations?**
A: No, Supervisors are restricted to their assigned cell/area (to be implemented with data filtering).

**Q: Is audit log permanent?**
A: Last 1000 entries are kept in browser storage. Admin can export for permanent backup.

**Q: What happens when server goes offline?**
A: Selected role is honored locally. All audit logs are stored locally and synced when server is back online.

---

## 📞 Support

For issues or questions about RBAC:
1. Check audit log for what happened
2. Verify your role has required permissions
3. Contact Administrator for role changes
4. Review this guide for permission details

---

**Last Updated:** August 13, 2024
**System Version:** 3.0 with RBAC
