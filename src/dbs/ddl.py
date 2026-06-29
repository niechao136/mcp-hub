"""
数据库 Schema 定义
表结构:
    - users            : 用户表
    - llm_models       : 支持的大模型配置 (provider 写死在代码中)
    - mcp_servers      : MCP Server 配置 (stdio / sse / streamable_http)
    - agents           : Agent 实例
    - agent_mcp_servers: Agent ↔ MCP Server 多对多绑定
    - agent_threads    : LangGraph checkpoint thread_id ↔ agent_id + user_id 映射
"""


DDL_UPDATE_MODIFIED_COLUMN = """
CREATE OR REPLACE FUNCTION update_modified_column()
    RETURNS TRIGGER AS
$$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;
"""

# ------------------------------------------------------------------ #

DDL_USERS = """
CREATE TABLE IF NOT EXISTS users
(
    id         UUID PRIMARY KEY         DEFAULT gen_random_uuid(),
    username   VARCHAR(50)  NOT NULL,
    email      VARCHAR(100),
    password   VARCHAR(255) NOT NULL,
    role       VARCHAR(20)  NOT NULL    DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
"""

DDL_USER_INDEXES = """
CREATE UNIQUE INDEX IF NOT EXISTS users_username_unique
    ON users (username)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_users_deleted_at
    ON users (deleted_at)
    WHERE deleted_at IS NULL;
"""

DDL_USER_TRIGGER = """
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_users_modified') THEN
        CREATE TRIGGER update_users_modified
            BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
    END IF;
END $$;
"""

# ------------------------------------------------------------------ #

DDL_LLM_MODELS = """
CREATE TABLE IF NOT EXISTS llm_models
(
    id                  UUID PRIMARY KEY         DEFAULT gen_random_uuid(),
    display_name        VARCHAR(100) NOT NULL,
    provider            VARCHAR(50)  NOT NULL,
    model_id            VARCHAR(200) NOT NULL,
    base_url            VARCHAR(500),
    api_key             TEXT,
    context_window      INT,
    max_tokens          INT,
    supports_tool_call  BOOLEAN      NOT NULL    DEFAULT TRUE,
    supports_vision     BOOLEAN      NOT NULL    DEFAULT FALSE,
    is_active           BOOLEAN      NOT NULL    DEFAULT TRUE,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP WITH TIME ZONE DEFAULT NULL
);
"""

DDL_LLM_MODELS_INDEXES = """
CREATE UNIQUE INDEX IF NOT EXISTS llm_models_provider_model_unique_active
    ON llm_models (provider, model_id)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_llm_models_deleted_at
    ON llm_models (deleted_at)
    WHERE deleted_at IS NULL;
"""

DDL_LLM_MODELS_TRIGGER = """
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_llm_models_modified') THEN
        CREATE TRIGGER update_llm_models_modified
            BEFORE UPDATE ON llm_models
            FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
    END IF;
END $$;
"""

# ------------------------------------------------------------------ #

DDL_MCP_SERVERS = """
CREATE TABLE IF NOT EXISTS mcp_servers
(
    id              UUID PRIMARY KEY         DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    transport       VARCHAR(20)  NOT NULL    DEFAULT 'sse',
    -- stdio
    command         VARCHAR(500),
    args            JSONB                    DEFAULT '[]',
    env             JSONB                    DEFAULT '{}',
    -- sse / streamable_http
    url             VARCHAR(500),
    headers         JSONB                    DEFAULT '{}',
    -- 健康状态
    status          VARCHAR(20)  NOT NULL    DEFAULT 'unknown',
    last_checked_at TIMESTAMP WITH TIME ZONE,
    -- 工具快照 (load_mcp_tools 返回的 schema 缓存)
    tools_cache     JSONB                    DEFAULT '[]',
    created_by      UUID         NOT NULL REFERENCES users (id),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at      TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    CONSTRAINT chk_transport_stdio   CHECK (transport != 'stdio'        OR command IS NOT NULL),
    CONSTRAINT chk_transport_network CHECK (transport  = 'stdio'        OR url     IS NOT NULL)
);
"""

DDL_MCP_SERVERS_INDEXES = """
CREATE UNIQUE INDEX IF NOT EXISTS mcp_servers_name_unique_active
    ON mcp_servers (name)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_mcp_servers_deleted_at
    ON mcp_servers (deleted_at)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_mcp_servers_status
    ON mcp_servers (status)
    WHERE deleted_at IS NULL;
"""

DDL_MCP_SERVERS_TRIGGER = """
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_mcp_servers_modified') THEN
        CREATE TRIGGER update_mcp_servers_modified
            BEFORE UPDATE ON mcp_servers
            FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
    END IF;
END $$;
"""

# ------------------------------------------------------------------ #

DDL_AGENTS = """
CREATE TABLE IF NOT EXISTS agents
(
    id              UUID PRIMARY KEY         DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    llm_model_id    UUID         NOT NULL REFERENCES llm_models (id),
    system_prompt   TEXT         NOT NULL    DEFAULT '',
    temperature     NUMERIC(3,2) NOT NULL    DEFAULT 0.00
                        CHECK (temperature >= 0 AND temperature <= 2),
    max_tokens      INT,
    -- 记忆策略: window | summary | full | none
    memory_strategy VARCHAR(20)  NOT NULL    DEFAULT 'window',
    memory_window   INT          NOT NULL    DEFAULT 20,
    is_active       BOOLEAN      NOT NULL    DEFAULT TRUE,
    created_by      UUID         NOT NULL REFERENCES users (id),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at      TIMESTAMP WITH TIME ZONE DEFAULT NULL
);
"""

DDL_AGENTS_INDEXES = """
CREATE UNIQUE INDEX IF NOT EXISTS agents_name_owner_unique_active
    ON agents (name, created_by)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_agents_created_by
    ON agents (created_by)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_agents_llm_model
    ON agents (llm_model_id)
    WHERE deleted_at IS NULL;
"""

DDL_AGENTS_TRIGGER = """
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_agents_modified') THEN
        CREATE TRIGGER update_agents_modified
            BEFORE UPDATE ON agents
            FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
    END IF;
END $$;
"""

# ------------------------------------------------------------------ #

DDL_AGENT_MCP_SERVERS = """
CREATE TABLE IF NOT EXISTS agent_mcp_servers
(
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id        UUID NOT NULL REFERENCES agents (id)      ON DELETE CASCADE,
    mcp_server_id   UUID NOT NULL REFERENCES mcp_servers (id) ON DELETE CASCADE,
    -- NULL 表示开放全部工具; 填写则为白名单过滤
    allowed_tools   JSONB        DEFAULT NULL,
    -- 同一 agent 下多个 MCP 的加载顺序
    priority        INT  NOT NULL DEFAULT 0,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_agent_mcp UNIQUE (agent_id, mcp_server_id)
);
"""

DDL_AGENT_MCP_SERVERS_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_agent_mcp_agent_id     ON agent_mcp_servers (agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_mcp_mcp_server_id ON agent_mcp_servers (mcp_server_id);
"""

# ------------------------------------------------------------------ #

DDL_AGENT_THREADS = """
CREATE TABLE IF NOT EXISTS agent_threads
(
    -- thread_id 即 LangGraph checkpointer 使用的 config["configurable"]["thread_id"]
    thread_id   VARCHAR(100) PRIMARY KEY,
    agent_id    UUID         NOT NULL REFERENCES agents (id) ON DELETE CASCADE,
    user_id     UUID         NOT NULL REFERENCES users (id),
    title       VARCHAR(200),
    -- 会话创建时的 agent 配置快照, 用于历史回放
    agent_snapshot  JSONB,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at  TIMESTAMP WITH TIME ZONE DEFAULT NULL
);
"""

DDL_AGENT_THREADS_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_agent_threads_agent_id
    ON agent_threads (agent_id)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_agent_threads_user_id
    ON agent_threads (user_id)
    WHERE deleted_at IS NULL;
"""

DDL_AGENT_THREADS_TRIGGER = """
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_agent_threads_modified') THEN
        CREATE TRIGGER update_agent_threads_modified
            BEFORE UPDATE ON agent_threads
            FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
    END IF;
END $$;
"""