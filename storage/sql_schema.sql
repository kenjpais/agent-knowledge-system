-- Optional metadata storage schema

CREATE TABLE IF NOT EXISTS features (
    feature_id TEXT PRIMARY KEY,
    summary TEXT,
    problem_statement TEXT,
    solution_summary TEXT,
    exec_scope TEXT,
    incomplete_feature BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feature_prs (
    feature_id TEXT,
    pr_id TEXT,
    FOREIGN KEY (feature_id) REFERENCES features(feature_id)
);

CREATE TABLE IF NOT EXISTS feature_jiras (
    feature_id TEXT,
    jira_id TEXT,
    FOREIGN KEY (feature_id) REFERENCES features(feature_id)
);

CREATE TABLE IF NOT EXISTS graph_nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT,
    title TEXT,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS graph_edges (
    from_node TEXT,
    to_node TEXT,
    edge_type TEXT,
    PRIMARY KEY (from_node, to_node),
    FOREIGN KEY (from_node) REFERENCES graph_nodes(node_id),
    FOREIGN KEY (to_node) REFERENCES graph_nodes(node_id)
);
