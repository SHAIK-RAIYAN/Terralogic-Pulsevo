-- PULSEVO Supabase Database Schema
-- Run this SQL in Supabase SQL Editor

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== USERS TABLE ====================
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    initials VARCHAR(5),
    role VARCHAR(50),
    team VARCHAR(50),
    avatar_url VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== TASKS TABLE ====================
CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    task_name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Open', 'In Progress', 'Completed', 'Blocked')),
    priority VARCHAR(20) CHECK (priority IN ('High', 'Medium', 'Low')),
    project VARCHAR(100),
    assigned_to VARCHAR(50) REFERENCES users(user_id) ON DELETE SET NULL,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date TIMESTAMP WITH TIME ZONE,
    start_date TIMESTAMP WITH TIME ZONE,
    completed_date TIMESTAMP WITH TIME ZONE,
    estimated_hours FLOAT,
    tags VARCHAR(200),
    blocked_reason VARCHAR(200),
    comments TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== INDEXES ====================
-- Indexes for better query performance

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_team ON users(team);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Tasks indexes
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_created_date ON tasks(created_date);
CREATE INDEX IF NOT EXISTS idx_tasks_completed_date ON tasks(completed_date);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tasks_status_project ON tasks(status, project);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_status ON tasks(assigned_to, status);

-- ==================== FUNCTIONS ====================
-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== ROW LEVEL SECURITY (RLS) ====================
-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated users (adjust as needed)
-- For hackathon, we'll allow all operations. In production, you'd want more restrictive policies.

-- Users policies
CREATE POLICY "Allow all operations on users" ON users
    FOR ALL USING (true) WITH CHECK (true);

-- Tasks policies
CREATE POLICY "Allow all operations on tasks" ON tasks
    FOR ALL USING (true) WITH CHECK (true);

-- ==================== REAL-TIME SUBSCRIPTIONS ====================
-- Enable real-time for both tables
ALTER PUBLICATION supabase_realtime ADD TABLE users;
ALTER PUBLICATION supabase_realtime ADD TABLE tasks;

-- ==================== COMMENTS ====================
COMMENT ON TABLE users IS 'Stores team member information';
COMMENT ON TABLE tasks IS 'Stores all task information with status, priority, and assignment details';

COMMENT ON COLUMN users.user_id IS 'Primary key: Unique user identifier (e.g., USER-001)';
COMMENT ON COLUMN users.team IS 'Team name (e.g., Your Team, Alpha Team)';
COMMENT ON COLUMN tasks.task_id IS 'Primary key: Unique task identifier (e.g., TASK-0001)';
COMMENT ON COLUMN tasks.status IS 'Task status: Open, In Progress, Completed, or Blocked';
COMMENT ON COLUMN tasks.assigned_to IS 'Foreign key reference to users.user_id';

