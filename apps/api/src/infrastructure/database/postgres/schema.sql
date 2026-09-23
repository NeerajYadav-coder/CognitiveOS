-- CognitiveOS Core Schema (PostgreSQL + pgvector)

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    profile_metadata JSONB DEFAULT '{}',
    cognition_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc')
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    session_context JSONB DEFAULT '{}',
    started_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    ended_at TIMESTAMP WITHOUT TIME ZONE
);

-- Cognitive Interactions
CREATE TABLE cognitive_interactions (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    raw_input TEXT NOT NULL,
    normalized_input TEXT,
    intent_output JSONB,
    cognitive_mode JSONB,
    ambiguity_score FLOAT,
    orchestration_trace JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc')
);

-- Semantic Memory (pgvector)
CREATE TABLE semantic_memories (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    content_id UUID NOT NULL,
    raw_content TEXT NOT NULL,
    embedding vector, -- Optimized for text-embedding-3-small / gpt-4o
    metadata_fields JSONB DEFAULT '{}'
);

-- Indices for performance
CREATE INDEX idx_semantic_memories_user_id ON semantic_memories(user_id);
CREATE INDEX idx_semantic_memories_content_type ON semantic_memories(content_type);
-- CREATE INDEX idx_semantic_memories_embedding ON semantic_memories USING hnsw (embedding vector_cosine_ops);

-- Reflections table
CREATE TABLE reflections (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    reflection_type VARCHAR(50),
    reflection_content JSONB,
    confidence FLOAT,
    generated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc')
);

-- Research Executions
CREATE TABLE research_executions (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    research_tree JSONB,
    exploration_paths JSONB,
    synthesis_state JSONB,
    execution_metadata JSONB
);

-- Workspace State
CREATE TABLE workspace_states (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    graph_layout JSONB,
    visual_state JSONB,
    semantic_filters JSONB,
    active_explorations JSONB
);
