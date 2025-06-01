CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    description TEXT,
    github_issue_id BIGINT NOT NULL,
    github_issue_url TEXT NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('open', 'notplanned', 'completed')),
    priority VARCHAR(50) NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
    assignee VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_github_issue_id ON tasks (github_issue_id);
CREATE INDEX idx_tasks_assignee ON tasks (assignee);