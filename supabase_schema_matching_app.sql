-- ============================================================
-- Elkayem Manpower Allocation — Supabase Schema
-- Matches EXACTLY the tables/columns used in server_advanced.py
-- Run in: Supabase Dashboard -> SQL Editor -> New Query -> Run
-- ============================================================

create table if not exists users (
    id            bigserial primary key,
    username      text unique not null,
    password_hash text not null,
    role          text default 'type1',
    email         text,
    active        int default 1,
    created_at    timestamptz default now()
);

create table if not exists sessions (
    id            bigserial primary key,
    user_id       bigint,
    token         text unique,
    expires_at    timestamptz,
    created_at    timestamptz default now()
);

create table if not exists employees (
    id            bigserial primary key,
    name          text not null,
    category      text,
    phone         text,
    skills        text,
    status        text default 'active',
    created_at    timestamptz default now(),
    updated_at    timestamptz default now()
);

create table if not exists allocations (
    id                bigserial primary key,
    cell_id           text not null,
    date              text not null,
    shift             int default 1,
    process_name      text not null,
    category          text,
    plan_count        int default 1,
    assigned_employee text,
    remark            text,
    status            text default 'pending',
    created_by        bigint,
    approval_status   text default 'pending',
    approved_by       bigint,
    approved_at       timestamptz,
    created_at        timestamptz default now(),
    updated_at        timestamptz default now(),
    unique(cell_id, date, shift, process_name)
);

create table if not exists attendance (
    id            bigserial primary key,
    date          text not null,
    shift         int default 1,
    employee_name text not null,
    process_name  text,
    cell          text,
    clock_in      text,
    clock_out     text,
    status        text default 'Present',
    created_at    timestamptz default now(),
    unique(date, shift, employee_name)
);

create table if not exists ot_logs (
    id            bigserial primary key,
    employee_name text not null,
    cell          text,
    date          text not null,
    hours         real default 0,
    reason        text,
    approved      text default 'pending',
    month         text,
    created_at    timestamptz default now()
);

create table if not exists gas_flow_audits (
    id            bigserial primary key,
    date          text not null,
    shift_block   text not null,
    cell_id       text,
    model_name    text,
    process_name  text,
    mc_no         text,
    mc_name       text,
    actual_flow   real,
    revised_flow  real,
    reading_name  text,
    reason        text,
    supervisor    text,
    created_by    bigint,
    created_at    timestamptz default now(),
    updated_at    timestamptz default now(),
    unique(date, shift_block, cell_id, process_name, mc_no)
);

create table if not exists production_targets (
    id            bigserial primary key,
    date          text not null,
    shift         int default 1,
    cell          text,
    product       text,
    target        int default 0,
    actual        int default 0,
    created_at    timestamptz default now(),
    unique(date, shift, cell)
);

create table if not exists leaves (
    id            bigserial primary key,
    employee_name text not null,
    leave_type    text,
    from_date     text,
    to_date       text,
    days          int default 1,
    reason        text,
    status        text default 'Pending',
    created_at    timestamptz default now()
);

create table if not exists skills (
    id            bigserial primary key,
    employee_name text unique not null,
    skill_list    text,
    experience    int default 1,
    score         int default 7,
    updated_at    timestamptz default now()
);

create table if not exists allocation_history (
    id                bigserial primary key,
    allocation_id     bigint,
    date              text,
    cell_id           text,
    process_name      text,
    assigned_employee text,
    status            text,
    shift             text,
    created_at        timestamptz default now()
);

-- ============================================================
-- Seed data (same defaults server_advanced.py inserts on first run)
-- ============================================================
insert into users (username, password_hash, role, email) values
 ('admin', encode(digest('admin123','sha256'),'hex'), 'admin', 'admin@elkayem.com'),
 ('supervisor', encode(digest('super123','sha256'),'hex'), 'supervisor', 'sup@elkayem.com'),
 ('operator', encode(digest('oper123','sha256'),'hex'), 'type1', 'op@elkayem.com')
on conflict (username) do nothing;

-- pgcrypto needed for the digest() function above
create extension if not exists pgcrypto;

insert into employees (name, category, phone, skills, status) values
 ('Rajesh Kumar','Robot Op','+91 9876543210','Robot Op, MIG Welding','active'),
 ('Priya Singh','Welder','+91 9876543211','MIG Welding, TIG Welding','active'),
 ('Amit Patel','Helper','+91 9876543212','Material Handling, Cleaning','active'),
 ('Neha Sharma','Operator','+91 9876543213','Boring, Revising, Inspection','active'),
 ('Suresh Reddy','Robot Op','+91 9876543214','Robot Op, FANUC','active'),
 ('Meena Devi','Helper','+91 9876543215','Spatter Cleaning','active'),
 ('Karthik Raja','Welder','+91 9876543216','Full Welding, Rework','active'),
 ('Divya Lakshmi','Operator','+91 9876543217','Gauge Inspection, Visual','active')
on conflict do nothing;

-- ============================================================
-- Indexes
-- ============================================================
create index if not exists idx_alloc_cell_date on allocations(cell_id, date);
create index if not exists idx_attendance_date on attendance(date, shift);
create index if not exists idx_ot_month on ot_logs(month);
create index if not exists idx_gasflow_date on gas_flow_audits(date);
create index if not exists idx_targets_date on production_targets(date, shift);
create index if not exists idx_leaves_from on leaves(from_date);

-- ============================================================
-- NOTE: RLS is left OFF. Your Python backend will use the
-- service_role key, which bypasses RLS entirely, so no policies
-- are required for this setup.
-- ============================================================
