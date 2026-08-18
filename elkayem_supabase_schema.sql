-- ============================================================
-- Elkayem Manpower Allocation — Supabase Schema
-- Run this in Supabase Dashboard -> SQL Editor -> New Query
-- ============================================================

-- Enable UUID generation
create extension if not exists "pgcrypto";

-- ------------------------------------------------------------
-- 1. EMPLOYEES
-- ------------------------------------------------------------
create table employees (
    id            uuid primary key default gen_random_uuid(),
    name          text not null,
    category      text not null,       -- Robot Operator, Welder, Helper, Operator, SPM Rotary
    phone         text,
    skills        text,                -- comma separated, or move to skill_matrix table
    status        text default 'Active', -- Active, Inactive, On Leave
    created_at    timestamptz default now(),
    updated_at    timestamptz default now()
);

-- ------------------------------------------------------------
-- 2. CELLS / LINES (reference table for the 11 production cells)
-- ------------------------------------------------------------
create table cells (
    id            serial primary key,
    name          text not null unique  -- e.g. "Cell 1 - N360 Swingarm"
);

insert into cells (name) values
 ('Cell 1 - N360 Swingarm'),
 ('Cell 2 - XL100 & U358 Swingarm'),
 ('Cell 3 - U347 Swingarm (Line-1)'),
 ('Cell 4 - U347 Swingarm (Line-2)'),
 ('Cell 5 - Sports & U223 Swingarm'),
 ('Cell 6 - Sports Swingarm Line-2'),
 ('Cell 7 - U546 Swingarm'),
 ('Cell 8 - U359 Swingarm'),
 ('Cell 9 - HLX125 & Star Swingarm Line-2'),
 ('Cell 10 - HLX & U237 Swingarm'),
 ('Cell 11 - Press Shop');

-- ------------------------------------------------------------
-- 3. MANPOWER ALLOCATION
-- ------------------------------------------------------------
create table allocations (
    id                uuid primary key default gen_random_uuid(),
    cell_id           int references cells(id),
    date              date not null,
    shift             text not null,     -- Shift 1 / 2 / 3
    s_no              int,
    process_name      text,
    category          text,
    plan              int,
    assigned_employee uuid references employees(id),
    remark            text,
    status            text default 'Pending',
    created_at        timestamptz default now(),
    updated_at        timestamptz default now()
);

-- ------------------------------------------------------------
-- 4. DAILY ATTENDANCE
-- ------------------------------------------------------------
create table attendance (
    id            uuid primary key default gen_random_uuid(),
    employee_id   uuid references employees(id),
    process_name  text,
    cell_id       int references cells(id),
    date          date not null,
    shift         text not null,
    clock_in      time,
    clock_out     time,
    status        text,          -- Present, Absent, Late, etc.
    created_at    timestamptz default now()
);

-- ------------------------------------------------------------
-- 5. OVERTIME TRACKER
-- ------------------------------------------------------------
create table overtime (
    id            uuid primary key default gen_random_uuid(),
    employee_id   uuid references employees(id),
    cell_id       int references cells(id),
    date          date not null,
    ot_hours      numeric(5,2),
    reason        text,
    approved      boolean default false,
    created_at    timestamptz default now()
);

-- ------------------------------------------------------------
-- 6. GAS FLOW AUDIT
-- ------------------------------------------------------------
create table gas_flow_audit (
    id                uuid primary key default gen_random_uuid(),
    cell_id           int references cells(id),
    date              date not null,
    model_name        text,
    process            text,
    machine_no        text,
    machine_name      text,
    shift             text,           -- Shift I 8:30AM / Shift I 3:00PM / Shift II 12:00AM
    actual_flow_lpm   numeric(5,2),
    revised_flow_lpm  numeric(5,2),
    reading_name      text,
    reason            text,
    supervisor        text,
    created_at        timestamptz default now()
);

-- ------------------------------------------------------------
-- 7. PRODUCTION TARGETS (Plan vs Actual)
-- ------------------------------------------------------------
create table production_targets (
    id            uuid primary key default gen_random_uuid(),
    cell_id       int references cells(id),
    date          date not null,
    shift         text,
    product       text,
    target        int,
    actual        int,
    created_at    timestamptz default now()
);

-- ------------------------------------------------------------
-- 8. LEAVE MANAGEMENT
-- ------------------------------------------------------------
create table leave_requests (
    id            uuid primary key default gen_random_uuid(),
    employee_id   uuid references employees(id),
    leave_type    text,        -- Casual, Sick, Emergency, Annual
    from_date     date,
    to_date       date,
    days          int,
    reason        text,
    status        text default 'Pending', -- Pending, Approved, Rejected
    created_at    timestamptz default now()
);

-- ------------------------------------------------------------
-- 9. SKILL MATRIX
-- ------------------------------------------------------------
create table skill_matrix (
    id            uuid primary key default gen_random_uuid(),
    employee_id   uuid references employees(id),
    category      text,
    skills        text,
    experience_years numeric(4,1),
    score         int check (score between 1 and 10),
    created_at    timestamptz default now()
);

-- ------------------------------------------------------------
-- 10. APPROVALS (pending allocation approvals)
-- ------------------------------------------------------------
create table approvals (
    id             uuid primary key default gen_random_uuid(),
    cell_id        int references cells(id),
    date           date,
    process_name   text,
    employee_id    uuid references employees(id),
    status         text default 'Pending',
    submitted_by   text,
    submitted_on   timestamptz default now()
);

-- ------------------------------------------------------------
-- 11. ALLOCATION HISTORY (log / audit trail)
-- ------------------------------------------------------------
create table allocation_history (
    id            uuid primary key default gen_random_uuid(),
    date          date,
    cell_id       int references cells(id),
    employee_id   uuid references employees(id),
    process_name  text,
    shift         text,
    status        text,
    created_at    timestamptz default now()
);

-- ------------------------------------------------------------
-- 12. SETTINGS (single row config table)
-- ------------------------------------------------------------
create table settings (
    id              int primary key default 1,
    company_name    text default 'Elkayem Auto Ancillaries',
    default_shift   text default 'Shift 1',
    theme           text default 'Dark Mode',
    constraint single_row check (id = 1)
);

insert into settings (id) values (1);

-- ============================================================
-- Helpful indexes for common lookups
-- ============================================================
create index idx_allocations_date_cell on allocations(date, cell_id);
create index idx_attendance_date_cell on attendance(date, cell_id);
create index idx_overtime_date on overtime(date);
create index idx_gas_flow_date on gas_flow_audit(date);
create index idx_production_targets_date on production_targets(date);
create index idx_leave_employee on leave_requests(employee_id);

-- ============================================================
-- NOTE ON ACCESS CONTROL (Row Level Security)
-- ============================================================
-- By default Supabase enables RLS once you turn it on, which blocks
-- all access until you add policies. Since your Python backend uses
-- the service_role key (which bypasses RLS entirely), you do NOT need
-- to enable RLS for this setup to work — your backend is the only
-- thing talking to Supabase, and it controls what each user can see.
--
-- If you ever want the frontend calling Supabase directly (skipping
-- your Python backend), you would need to enable RLS and write
-- policies per table. Not needed for your current architecture.
