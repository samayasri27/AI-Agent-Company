-- Centralized Memory System Database Schema
-- This script creates all necessary tables and indexes for the memory system

-- Enable pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Agents table for reference
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Knowledge storage table
CREATE TABLE IF NOT EXISTS knowledge_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('structured', 'unstructured')),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536), -- OpenAI embedding dimension
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversation history table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    thread_id VARCHAR(255),
    message TEXT NOT NULL,
    role VARCHAR(50) CHECK (role IN ('user', 'assistant', 'system')),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Action history table
CREATE TABLE IF NOT EXISTS actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    success BOOLEAN DEFAULT TRUE,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Learning patterns table
CREATE TABLE IF NOT EXISTS learning_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    task_type VARCHAR(100) NOT NULL,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_execution_time_ms INTEGER,
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(agent_id, task_type)
);

-- Create indexes for performance optimization

-- Vector similarity search index
CREATE INDEX IF NOT EXISTS knowledge_embedding_idx 
ON knowledge_entries 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Agent-based indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_knowledge_agent_id ON knowledge_entries(agent_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_content_type ON knowledge_entries(content_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_created_at ON knowledge_entries(created_at);

CREATE INDEX IF NOT EXISTS idx_conversations_agent_id ON conversations(agent_id);
CREATE INDEX IF NOT EXISTS idx_conversations_thread_id ON conversations(thread_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);

CREATE INDEX IF NOT EXISTS idx_actions_agent_id ON actions(agent_id);
CREATE INDEX IF NOT EXISTS idx_actions_type ON actions(action_type);
CREATE INDEX IF NOT EXISTS idx_actions_success ON actions(success);
CREATE INDEX IF NOT EXISTS idx_actions_created_at ON actions(created_at);

CREATE INDEX IF NOT EXISTS idx_learning_agent_task ON learning_patterns(agent_id, task_type);
CREATE INDEX IF NOT EXISTS idx_learning_last_updated ON learning_patterns(last_updated);

-- Create some sample data for development and testing
INSERT INTO agents (name, department, role) VALUES 
    ('CEO Agent', 'executive', 'ceo'),
    ('Developer Agent', 'engineering', 'developer'),
    ('Marketing Agent', 'marketing', 'marketing_specialist'),
    ('Finance Agent', 'finance', 'financial_analyst')
ON CONFLICT DO NOTHING;

-- Add comments for documentation
COMMENT ON TABLE agents IS 'Stores information about AI agents in the system';
COMMENT ON TABLE knowledge_entries IS 'Stores structured and unstructured knowledge with vector embeddings';
COMMENT ON TABLE conversations IS 'Stores conversation history between agents and users';
COMMENT ON TABLE actions IS 'Logs all actions performed by agents with input/output data';
COMMENT ON TABLE learning_patterns IS 'Tracks learning patterns and success metrics for different task types';

COMMENT ON COLUMN knowledge_entries.embedding IS 'Vector embedding for semantic similarity search using pgvector';
COMMENT ON COLUMN knowledge_entries.content_type IS 'Type of content: structured or unstructured';
COMMENT ON COLUMN conversations.role IS 'Role in conversation: user, assistant, or system';
COMMENT ON COLUMN actions.execution_time_ms IS 'Time taken to execute the action in milliseconds';
COMMENT ON COLUMN learning_patterns.avg_execution_time_ms IS 'Average execution time for this task type';