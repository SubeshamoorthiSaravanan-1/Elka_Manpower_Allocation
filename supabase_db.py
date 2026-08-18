"""
NEW FILE - does not modify any existing project files.

SupabaseDatabase mirrors the exact same public method names and
signatures as the `Database` class in server_advanced.py, so it can
be used as a drop-in replacement.

To switch the app to Supabase, the ONLY change needed in
server_advanced.py is this one line (not made automatically, since
you asked not to touch existing code):

    class APIHandler(BaseHTTPRequestHandler):
        db = Database(DB_FILE)              # <- current line

becomes:

    from supabase_db import SupabaseDatabase
    class APIHandler(BaseHTTPRequestHandler):
        db = SupabaseDatabase()              # <- new line

Everything else in server_advanced.py (routes, request handling,
auth headers, JSON responses) stays exactly as-is, because this
class returns the same shapes of data (list of dicts / dicts) that
the existing routes already expect.
"""
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from supabase_client import supabase


class SupabaseDatabase:
    def __init__(self):
        # Table creation happens once via supabase_schema_matching_app.sql
        # in the Supabase SQL Editor, not here.
        pass

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    # ── auth / sessions ──
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        res = (
            supabase.table("users")
            .select("*")
            .eq("username", username)
            .eq("password_hash", self.hash_password(password))
            .eq("active", 1)
            .execute()
        )
        return res.data[0] if res.data else None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        res = supabase.table("users").select("*").eq("id", user_id).execute()
        return res.data[0] if res.data else None

    def create_session(self, user_id: int) -> str:
        token = hashlib.sha256(f"{user_id}{time.time()}".encode()).hexdigest()
        expires_at = (datetime.now() + timedelta(days=7)).isoformat()
        supabase.table("sessions").insert(
            {"user_id": user_id, "token": token, "expires_at": expires_at}
        ).execute()
        return token

    def verify_token(self, token: str) -> Optional[int]:
        now = datetime.now().isoformat()
        res = (
            supabase.table("sessions")
            .select("user_id")
            .eq("token", token)
            .gt("expires_at", now)
            .execute()
        )
        return res.data[0]["user_id"] if res.data else None

    # ── employees ──
    def get_employees(self) -> List[Dict]:
        res = supabase.table("employees").select("*").order("name").execute()
        return res.data

    def add_employee(self, name, category, phone, skills, status) -> int:
        res = (
            supabase.table("employees")
            .insert({"name": name, "category": category, "phone": phone,
                     "skills": skills, "status": status})
            .execute()
        )
        return res.data[0]["id"]

    def update_employee(self, emp_id, name, category, phone, skills, status):
        supabase.table("employees").update({
            "name": name, "category": category, "phone": phone,
            "skills": skills, "status": status,
            "updated_at": datetime.now().isoformat()
        }).eq("id", emp_id).execute()

    def delete_employee(self, emp_id: int):
        supabase.table("employees").delete().eq("id", emp_id).execute()

    # ── allocations ──
    def save_allocation(self, cell_id, date, shift, rows, user_id):
        for row in rows:
            supabase.table("allocations").upsert({
                "cell_id": cell_id, "date": date, "shift": shift,
                "process_name": row.get("process", ""),
                "category": row.get("category", ""),
                "plan_count": row.get("plan", 1),
                "assigned_employee": row.get("assigned", ""),
                "remark": row.get("remark", ""),
                "status": row.get("status", "pending"),
                "approval_status": "pending",
                "created_by": user_id
            }, on_conflict="cell_id,date,shift,process_name").execute()

            if row.get("assigned", "").strip():
                supabase.table("allocation_history").insert({
                    "date": date, "cell_id": cell_id,
                    "process_name": row.get("process", ""),
                    "assigned_employee": row.get("assigned", ""),
                    "status": row.get("status", "pending"),
                    "shift": shift
                }).execute()

    def get_allocations(self, cell_id=None, date=None) -> List[Dict]:
        q = supabase.table("allocations").select("*")
        if cell_id:
            q = q.eq("cell_id", cell_id)
        if date:
            q = q.eq("date", date)
        return q.execute().data

    def get_allocation_history(self, date=None, cell_id=None) -> List[Dict]:
        q = supabase.table("allocation_history").select("*")
        if date:
            q = q.eq("date", date)
        if cell_id:
            q = q.eq("cell_id", cell_id)
        res = q.order("created_at", desc=True).limit(500).execute()
        return res.data

    def get_pending_approvals(self) -> List[Dict]:
        res = (
            supabase.table("allocations")
            .select("*")
            .eq("approval_status", "pending")
            .order("created_at", desc=True)
            .limit(500)
            .execute()
        )
        return res.data

    def approve_allocation(self, allocation_id: int, approved_by: int) -> bool:
        try:
            supabase.table("allocations").update({
                "approval_status": "approved",
                "approved_by": approved_by,
                "approved_at": datetime.now().isoformat()
            }).eq("id", allocation_id).execute()
            return True
        except Exception as e:
            print(f"Error approving allocation: {e}")
            return False

    def reject_allocation(self, allocation_id: int, approved_by: int) -> bool:
        try:
            supabase.table("allocations").update({
                "approval_status": "rejected",
                "approved_by": approved_by,
                "approved_at": datetime.now().isoformat()
            }).eq("id", allocation_id).execute()
            return True
        except Exception as e:
            print(f"Error rejecting allocation: {e}")
            return False

    # ── attendance ──
    def save_attendance(self, date, shift, rows):
        for r in rows:
            supabase.table("attendance").upsert({
                "date": date, "shift": shift,
                "employee_name": r.get("name", ""),
                "process_name": r.get("process", ""),
                "cell": r.get("cell", ""),
                "clock_in": r.get("clockIn", ""),
                "clock_out": r.get("clockOut", ""),
                "status": r.get("status", "Present")
            }, on_conflict="date,shift,employee_name").execute()

    def get_attendance(self, date=None, shift=None) -> List[Dict]:
        q = supabase.table("attendance").select("*")
        if date:
            q = q.eq("date", date)
        if shift:
            q = q.eq("shift", shift)
        return q.execute().data

    # ── OT logs ──
    def save_ot(self, month, rows):
        supabase.table("ot_logs").delete().eq("month", month).execute()
        for r in rows:
            supabase.table("ot_logs").insert({
                "employee_name": r.get("name", ""), "cell": r.get("cell", ""),
                "date": r.get("date", ""), "hours": r.get("hours", 0),
                "reason": r.get("reason", ""),
                "approved": r.get("approved", "pending"), "month": month
            }).execute()

    def get_ot(self, month=None) -> List[Dict]:
        q = supabase.table("ot_logs").select("*")
        if month:
            q = q.eq("month", month)
        res = q.order("date", desc=True).execute()
        return res.data

    # ── gas flow ──
    def save_gas_flow_audit(self, date, shift_block, rows, user_id):
        for row in rows:
            supabase.table("gas_flow_audits").upsert({
                "date": date, "shift_block": shift_block,
                "cell_id": row.get("cell", ""), "model_name": row.get("model", ""),
                "process_name": row.get("process", ""), "mc_no": row.get("mcNo", ""),
                "mc_name": row.get("mcName", ""), "actual_flow": row.get("actualFlow"),
                "revised_flow": row.get("revisedFlow"), "reading_name": row.get("name", ""),
                "reason": row.get("reason", ""), "supervisor": row.get("supervisor", ""),
                "created_by": user_id
            }, on_conflict="date,shift_block,cell_id,process_name,mc_no").execute()

    def get_gas_flow_audit(self, date=None) -> List[Dict]:
        q = supabase.table("gas_flow_audits").select("*")
        if date:
            q = q.eq("date", date)
        return q.execute().data

    # ── targets ──
    def save_targets(self, date, shift, rows):
        for r in rows:
            supabase.table("production_targets").upsert({
                "date": date, "shift": shift, "cell": r.get("cell"),
                "product": r.get("product", ""), "target": r.get("target", 0),
                "actual": r.get("actual", 0)
            }, on_conflict="date,shift,cell").execute()

    def get_targets(self, date=None, shift=None) -> List[Dict]:
        q = supabase.table("production_targets").select("*")
        if date:
            q = q.eq("date", date)
        if shift:
            q = q.eq("shift", shift)
        return q.execute().data

    # ── leaves ──
    def add_leave(self, emp, leave_type, from_date, to_date, days, reason, status) -> int:
        res = supabase.table("leaves").insert({
            "employee_name": emp, "leave_type": leave_type,
            "from_date": from_date, "to_date": to_date, "days": days,
            "reason": reason, "status": status
        }).execute()
        return res.data[0]["id"]

    def get_leaves(self, month=None) -> List[Dict]:
        res = supabase.table("leaves").select("*").order("created_at", desc=True).execute()
        rows = res.data
        if month:
            rows = [r for r in rows if (r.get("from_date") or "")[:7] == month]
        return rows

    def set_leave_status(self, leave_id, status):
        supabase.table("leaves").update({"status": status}).eq("id", leave_id).execute()

    def delete_leave(self, leave_id):
        supabase.table("leaves").delete().eq("id", leave_id).execute()

    # ── skills ──
    def save_skill(self, employee_name, skill_list, experience, score):
        supabase.table("skills").upsert({
            "employee_name": employee_name, "skill_list": skill_list,
            "experience": experience, "score": score,
            "updated_at": datetime.now().isoformat()
        }, on_conflict="employee_name").execute()

    def get_skills(self) -> List[Dict]:
        res = supabase.table("skills").select("*").order("employee_name").execute()
        return res.data

    # ── analytics / reports ──
    def get_analytics(self) -> Dict:
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")

        total_employees = len(supabase.table("employees").select("id").execute().data)
        today_allocs = supabase.table("allocations").select("*").eq("date", today).execute().data
        allocations_today = len(today_allocs)
        filled = len([a for a in today_allocs if a.get("assigned_employee")])
        ot_rows = supabase.table("ot_logs").select("hours").eq("month", month).execute().data
        ot_hours = sum(r.get("hours") or 0 for r in ot_rows)
        absent = len(
            supabase.table("attendance").select("id")
            .eq("date", today).eq("status", "Absent").execute().data
        )
        on_leave = len(
            supabase.table("leaves").select("id")
            .eq("status", "Approved").lte("from_date", today).gte("to_date", today)
            .execute().data
        )
        util = round(filled / allocations_today * 100, 1) if allocations_today > 0 else 0

        return {
            "totalEmployees": total_employees,
            "allocationsToday": allocations_today,
            "avgUtilization": util,
            "otHours": float(ot_hours),
            "absentToday": absent,
            "onLeave": on_leave
        }

    def get_monthly_report(self, month: str) -> List[Dict]:
        rows = []
        for c in range(1, 12):
            cell_str = str(c)
            allocs = (
                supabase.table("allocations").select("*")
                .eq("cell_id", cell_str).execute().data
            )
            allocs = [a for a in allocs if (a.get("date") or "")[:7] == month]
            total = len(allocs)
            filled = len([a for a in allocs if a.get("assigned_employee")])
            absent = len([a for a in allocs if a.get("remark") == "Absent"])
            ot_rows = (
                supabase.table("ot_logs").select("hours")
                .eq("cell", cell_str).eq("month", month).execute().data
            )
            ot = sum(r.get("hours") or 0 for r in ot_rows)
            util = round(filled / total * 100, 1) if total > 0 else 0
            rows.append({"cell": c, "total": total, "filled": filled, "absent": absent,
                         "otHours": float(ot), "util": util})
        return rows
