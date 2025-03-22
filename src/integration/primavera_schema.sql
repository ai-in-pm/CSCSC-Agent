-- Primavera P6 Integration - Database Schema
-- Advanced relational schema for storing and analyzing Primavera P6 project data

-- Projects table stores high-level project information from Primavera P6
CREATE TABLE IF NOT EXISTS primavera_projects (
    proj_id TEXT PRIMARY KEY,
    proj_name TEXT NOT NULL,
    proj_short_name TEXT,
    wbs_id TEXT,
    status_code TEXT,
    priority INTEGER,
    orig_proj_id TEXT,
    source_type TEXT,
    target_start_date TEXT,
    target_end_date TEXT,
    act_start_date TEXT,
    act_end_date TEXT,
    anticipated_start_date TEXT,
    anticipated_end_date TEXT,
    last_update_date TEXT,
    progress REAL DEFAULT 0,
    est_completion_date TEXT,
    total_activities INTEGER DEFAULT 0,
    completed_activities INTEGER DEFAULT 0,
    in_progress_activities INTEGER DEFAULT 0,
    not_started_activities INTEGER DEFAULT 0,
    budget_at_completion REAL,
    actual_cost REAL,
    forecast_cost REAL,
    raw_data TEXT,  -- JSON blob for additional data
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Activities table for individual schedule items from P6
CREATE TABLE IF NOT EXISTS primavera_activities (
    activity_id TEXT PRIMARY KEY,
    proj_id TEXT NOT NULL,
    activity_name TEXT NOT NULL,
    activity_code TEXT,
    wbs_id TEXT,
    status_code TEXT,
    type_code TEXT,
    calendar_id TEXT,
    total_float REAL,
    free_float REAL,
    remain_duration REAL,
    target_start_date TEXT,
    target_end_date TEXT,
    act_start_date TEXT,
    act_end_date TEXT,
    target_duration REAL,
    act_duration REAL,
    remain_early_start_date TEXT,
    remain_early_end_date TEXT,
    remain_late_start_date TEXT,
    remain_late_end_date TEXT,
    constraint_type TEXT,
    constraint_date TEXT,
    progress REAL DEFAULT 0,
    critical BOOLEAN DEFAULT 0,
    priority INTEGER,
    location_id TEXT,
    resource_ids TEXT,  -- Comma-separated list of assigned resource IDs
    predecessor_ids TEXT,  -- Comma-separated list of predecessor activity IDs
    successor_ids TEXT,  -- Comma-separated list of successor activity IDs
    raw_data TEXT,  -- JSON blob for additional data
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (proj_id) REFERENCES primavera_projects(proj_id) ON DELETE CASCADE
);

-- Resources table for P6 resources
CREATE TABLE IF NOT EXISTS primavera_resources (
    resource_id TEXT PRIMARY KEY,
    resource_name TEXT NOT NULL,
    resource_code TEXT,
    resource_type TEXT,
    max_units REAL,
    unit_type TEXT,
    calendar_id TEXT,
    cost_per_qty REAL,
    cost_per_qty2 REAL,
    cost_per_qty3 REAL,
    cost_per_qty4 REAL,
    cost_per_qty5 REAL,
    raw_data TEXT,  -- JSON blob for additional data
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Resource assignments linking activities to resources with specific assignments
CREATE TABLE IF NOT EXISTS primavera_resource_assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    proj_id TEXT NOT NULL,
    planned_units REAL,
    actual_units REAL,
    remain_units REAL,
    planned_cost REAL,
    actual_cost REAL,
    remain_cost REAL,
    target_start_date TEXT,
    target_end_date TEXT,
    act_start_date TEXT,
    act_end_date TEXT,
    raw_data TEXT,  -- JSON blob for additional data
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (activity_id) REFERENCES primavera_activities(activity_id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES primavera_resources(resource_id) ON DELETE CASCADE,
    FOREIGN KEY (proj_id) REFERENCES primavera_projects(proj_id) ON DELETE CASCADE
);

-- WBS (Work Breakdown Structure) table for P6 project structure
CREATE TABLE IF NOT EXISTS primavera_wbs (
    wbs_id TEXT PRIMARY KEY,
    proj_id TEXT NOT NULL,
    parent_wbs_id TEXT,
    wbs_name TEXT NOT NULL,
    wbs_short_name TEXT,
    seq_num INTEGER,
    status_code TEXT,
    wbs_level INTEGER,
    start_date TEXT,
    end_date TEXT,
    anticipated_start_date TEXT,
    anticipated_end_date TEXT,
    raw_data TEXT,  -- JSON blob for additional data
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (proj_id) REFERENCES primavera_projects(proj_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_wbs_id) REFERENCES primavera_wbs(wbs_id)
);

-- Calendars table for P6 calendars
CREATE TABLE IF NOT EXISTS primavera_calendars (
    calendar_id TEXT PRIMARY KEY,
    calendar_name TEXT NOT NULL,
    type_code TEXT,
    default_flag BOOLEAN DEFAULT 0,
    proj_id TEXT,
    standard_work_week TEXT,  -- JSON representation of standard work week
    holidays TEXT,  -- JSON array of holiday dates
    exceptions TEXT,  -- JSON array of calendar exceptions
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (proj_id) REFERENCES primavera_projects(proj_id) ON DELETE CASCADE
);

-- Table to track import operations
CREATE TABLE IF NOT EXISTS primavera_import_logs (
    import_id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_type TEXT NOT NULL,  -- 'api', 'database', 'file'
    source TEXT,  -- Source description or identifier
    status TEXT NOT NULL,  -- 'success', 'error', 'partial'
    message TEXT,
    start_time TEXT DEFAULT (datetime('now')),
    end_time TEXT,
    duration_sec REAL,
    metadata TEXT,  -- JSON blob with import statistics
    created_at TEXT DEFAULT (datetime('now'))
);

-- Table to store AI query history
CREATE TABLE IF NOT EXISTS primavera_ai_queries (
    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    query_text TEXT NOT NULL,
    response_text TEXT,
    query_type TEXT,  -- Classified query type (e.g., 'late_activities', 'progress', etc.)
    confidence_score REAL,
    execution_time_ms INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_primavera_activities_proj_id ON primavera_activities(proj_id);
CREATE INDEX IF NOT EXISTS idx_primavera_activities_critical ON primavera_activities(critical);
CREATE INDEX IF NOT EXISTS idx_primavera_activities_status ON primavera_activities(status_code);
CREATE INDEX IF NOT EXISTS idx_primavera_resource_assignments_proj_id ON primavera_resource_assignments(proj_id);
CREATE INDEX IF NOT EXISTS idx_primavera_resource_assignments_resource_id ON primavera_resource_assignments(resource_id);
CREATE INDEX IF NOT EXISTS idx_primavera_wbs_proj_id ON primavera_wbs(proj_id);
CREATE INDEX IF NOT EXISTS idx_primavera_wbs_parent_id ON primavera_wbs(parent_wbs_id);
