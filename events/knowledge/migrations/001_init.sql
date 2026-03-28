CREATE TABLE IF NOT EXISTS intel_items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_url TEXT,
    published_at TEXT,
    collected_at TEXT NOT NULL,
    capability TEXT,
    confidence_level TEXT NOT NULL DEFAULT 'medium',
    validated_status TEXT NOT NULL DEFAULT 'unreviewed',
    status TEXT NOT NULL DEFAULT 'staged'
);

CREATE TABLE IF NOT EXISTS knowledge_entries (
    id TEXT PRIMARY KEY,
    entry_type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    body_markdown TEXT NOT NULL DEFAULT '',
    primary_capability TEXT,
    tool_name TEXT,
    confidence_level TEXT NOT NULL DEFAULT 'medium',
    validated_status TEXT NOT NULL DEFAULT 'unreviewed',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intel_items_capability_published
ON intel_items(capability, published_at DESC);

CREATE INDEX IF NOT EXISTS idx_knowledge_entries_capability_updated
ON knowledge_entries(primary_capability, updated_at DESC);
