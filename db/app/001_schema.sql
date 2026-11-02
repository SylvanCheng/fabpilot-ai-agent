-- FabPilot application DB: everything the agent itself owns.
-- Kept minimal in P0; tables grow with P1 (chat loop), P4 (RAG) and P5 (auth/audit).

CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS app;
SET search_path = app, public;

CREATE TABLE app_user (
    user_id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    username      text NOT NULL UNIQUE,
    display_name  text NOT NULL,
    role          text NOT NULL DEFAULT 'engineer',   -- engineer / manager / admin
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE conversation (
    conversation_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          uuid NOT NULL REFERENCES app_user,
    title            text,
    created_at       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE message (
    message_id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id  uuid NOT NULL REFERENCES conversation ON DELETE CASCADE,
    role             text NOT NULL,                   -- user / assistant / tool / system
    content          text NOT NULL,
    created_at       timestamptz NOT NULL DEFAULT now()
);

-- Every tool call / SQL the agent runs, for audit and later evals.
CREATE TABLE tool_call (
    tool_call_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id    uuid REFERENCES message ON DELETE CASCADE,
    tool_name     text NOT NULL,
    arguments     jsonb NOT NULL,
    result_meta   jsonb,                              -- row count, duration, error; not raw data
    started_at    timestamptz NOT NULL DEFAULT now(),
    duration_ms   integer
);

-- RAG (P4): source documents and embedded chunks.
CREATE TABLE document (
    document_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title        text NOT NULL,
    source_uri   text,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE document_chunk (
    chunk_id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id  uuid NOT NULL REFERENCES document ON DELETE CASCADE,
    chunk_index  integer NOT NULL,
    content      text NOT NULL,
    embedding    vector(1024),                        -- bge-m3 dims; change with the embedding model
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX ON message (conversation_id, created_at);
CREATE INDEX ON document_chunk USING hnsw (embedding vector_cosine_ops);
