# File: migrations/001_initial.sql
-- Initial database schema for Dev Digest
-- This file creates the core tables needed for the application

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    github_username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    repositories TEXT, -- JSON array of repo names
    languages TEXT,    -- JSON array of languages
    stackoverflow_tags TEXT, -- JSON array of tags
    max_items_per_section INTEGER DEFAULT 5,
    digest_time VARCHAR(5) DEFAULT '20:00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Digest history table
CREATE TABLE IF NOT EXISTS digest_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'sent', -- sent, failed, skipped
    items_count INTEGER DEFAULT 0,
    error_message TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_github_username ON users(github_username);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_digest_history_user_id ON digest_history(user_id);
CREATE INDEX IF NOT EXISTS idx_digest_history_sent_at ON digest_history(sent_at);
CREATE INDEX IF NOT EXISTS idx_digest_history_status ON digest_history(status);

-- Insert default admin user (optional)
-- INSERT OR IGNORE INTO users (name, github_username, email, is_active)
-- VALUES ('Admin', 'admin', 'admin@devdigest.com', TRUE);