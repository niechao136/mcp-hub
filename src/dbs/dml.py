"""
DML 语句
"""


DML_INIT_USER = """
INSERT INTO users (username, password, role)
SELECT %s, %s, 'admin'
WHERE NOT EXISTS (
    SELECT 1
    FROM users
    WHERE username = %s AND deleted_at IS NULL
);
"""


DML_USER_REGISTER = """
INSERT INTO users (username, password, email, role)
VALUES (%s, %s, %s, 'user')
ON CONFLICT (username) WHERE deleted_at IS NULL DO NOTHING
RETURNING id, username, email, role, created_at;
"""


DML_USER_GET_BY_USERNAME = """
SELECT id, username, email, role, created_at, updated_at
FROM users
WHERE username = %s AND deleted_at IS NULL;
"""


DML_USER_GET_BY_USERNAME_WITH_PWD = """
SELECT id, username, email, role, password, created_at, updated_at
FROM users
WHERE username = %s AND deleted_at IS NULL;
"""


DML_USER_GET_BY_ID = """
SELECT id, username, email, role, created_at, updated_at
FROM users
WHERE id = %s AND deleted_at IS NULL;
"""


DML_USER_GET_BY_ID_WITH_PWD = """
SELECT id, username, email, role, password, created_at, updated_at
FROM users
WHERE id = %s AND deleted_at IS NULL;
"""


DML_USER_LIST = """
SELECT id, username, email, role, created_at, updated_at
FROM users
WHERE deleted_at IS NULL
    AND (
        %s IS NULL
        OR username ILIKE %s
        OR email ILIKE %s
    )
ORDER BY {order_by} {direction}
LIMIT %s OFFSET %s;
"""


DML_USER_COUNT = """
SELECT COUNT(*) AS total
FROM users
WHERE deleted_at IS NULL;
"""


DML_USER_CREATE = """
INSERT INTO users (username, password, email, role)
VALUES (%s, %s, %s, %s)
ON CONFLICT (username) WHERE deleted_at IS NULL DO NOTHING
RETURNING id, username, email, role, created_at;
"""


DML_USER_UPDATE = """
UPDATE users
SET username = %s, email = %s, role = %s
WHERE id = %s AND deleted_at IS NULL
RETURNING id, username, email, role, updated_at;
"""


DML_USER_DELETE = """
UPDATE users
SET deleted_at = NOW()
WHERE id = ANY(%s) AND deleted_at IS NULL
RETURNING id, username;
"""


DML_USER_UPDATE_PASSWORD = """
UPDATE users
SET password = %s
WHERE id = %s AND deleted_at IS NULL
RETURNING id;
"""


DML_LLM_MODEL_LIST = """
SELECT id, display_name, provider, model_id, base_url, context_window, max_tokens, supports_tool_call, supports_vision, is_active, created_at, updated_at
FROM llm_models
WHERE deleted_at IS NULL
ORDER BY {order_by} {direction}
LIMIT %s OFFSET %s;
"""


DML_LLM_MODEL_COUNT = """
SELECT COUNT(*) AS total
FROM llm_models
WHERE deleted_at IS NULL;
"""


DML_LLM_MODEL_GET_BY_ID = """
SELECT id, display_name, provider, model_id, base_url, context_window, max_tokens, supports_tool_call, supports_vision, is_active, created_at, updated_at
FROM llm_models
WHERE id = %s AND deleted_at IS NULL;
"""


DML_LLM_MODEL_GET_BY_ID_WITH_KEY = """
SELECT id, display_name, provider, model_id, base_url, api_key, context_window, max_tokens, supports_tool_call, supports_vision, is_active, created_at, updated_at
FROM llm_models
WHERE id = %s AND deleted_at IS NULL;
"""


DML_LLM_MODEL_GET_BY_PROVIDER_MODEL = """
SELECT id, display_name, provider, model_id, base_url, context_window, max_tokens, supports_tool_call, supports_vision, is_active, created_at, updated_at
FROM llm_models
WHERE provider = %s AND model_id = %s AND deleted_at IS NULL;
"""


DML_LLM_MODEL_CREATE = """
INSERT INTO llm_models (display_name, provider, model_id, base_url, api_key, context_window, max_tokens, supports_tool_call, supports_vision, is_active)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (provider, model_id) WHERE deleted_at IS NULL DO NOTHING
RETURNING id, display_name, provider, model_id, base_url, context_window, max_tokens, supports_tool_call, supports_vision, is_active, created_at;
"""


DML_LLM_MODEL_UPDATE = """
UPDATE llm_models
SET display_name = %s, provider = %s, model_id = %s, base_url = %s, api_key = %s, context_window = %s, max_tokens = %s, supports_tool_call = %s, supports_vision = %s, is_active = %s
WHERE id = %s AND deleted_at IS NULL
RETURNING id, display_name, provider, model_id, base_url, context_window, max_tokens, supports_tool_call, supports_vision, is_active, updated_at;
"""


DML_LLM_MODEL_DELETE = """
UPDATE llm_models
SET deleted_at = NOW()
WHERE id = ANY(%s) AND deleted_at IS NULL
RETURNING id, display_name;
"""


DML_LLM_MODEL_LIST_ACTIVE = """
SELECT id, display_name, provider, model_id, base_url, context_window, max_tokens, supports_tool_call, supports_vision, is_active, created_at, updated_at
FROM llm_models
WHERE deleted_at IS NULL AND is_active = TRUE
ORDER BY created_at DESC;
"""


DML_MCP_SERVER_LIST = """
SELECT id, name, description, transport, command, args, env, url, headers, status, last_checked_at, tools_cache, created_by, created_at, updated_at
FROM mcp_servers
WHERE deleted_at IS NULL
ORDER BY {order_by} {direction}
LIMIT %s OFFSET %s;
"""


DML_MCP_SERVER_COUNT = """
SELECT COUNT(*) AS total
FROM mcp_servers
WHERE deleted_at IS NULL;
"""


DML_MCP_SERVER_GET_BY_ID = """
SELECT id, name, description, transport, command, args, env, url, headers, status, last_checked_at, tools_cache, created_by, created_at, updated_at
FROM mcp_servers
WHERE id = %s AND deleted_at IS NULL;
"""


DML_MCP_SERVER_GET_BY_NAME = """
SELECT id, name, description, transport, command, args, env, url, headers, status, last_checked_at, tools_cache, created_by, created_at, updated_at
FROM mcp_servers
WHERE name = %s AND deleted_at IS NULL;
"""


DML_MCP_SERVER_CREATE = """
INSERT INTO mcp_servers (name, description, transport, command, args, env, url, headers, status, created_by)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (name) WHERE deleted_at IS NULL DO NOTHING
RETURNING id, name, description, transport, command, args, env, url, headers, status, last_checked_at, tools_cache, created_by, created_at;
"""


DML_MCP_SERVER_UPDATE = """
UPDATE mcp_servers
SET name = %s, description = %s, transport = %s, command = %s, args = %s, env = %s, url = %s, headers = %s
WHERE id = %s AND deleted_at IS NULL
RETURNING id, name, description, transport, command, args, env, url, headers, status, last_checked_at, tools_cache, created_by, updated_at;
"""


DML_MCP_SERVER_DELETE = """
UPDATE mcp_servers
SET deleted_at = NOW()
WHERE id = ANY(%s) AND deleted_at IS NULL
RETURNING id, name;
"""


DML_MCP_SERVER_LIST_ACTIVE = """
SELECT id, name, description, transport, command, args, env, url, headers, status, last_checked_at, tools_cache, created_by, created_at, updated_at
FROM mcp_servers
WHERE deleted_at IS NULL
ORDER BY created_at DESC;
"""


DML_MCP_SERVER_UPDATE_STATUS = """
UPDATE mcp_servers
SET status = %s, last_checked_at = NOW()
WHERE id = %s AND deleted_at IS NULL
RETURNING id, status, last_checked_at;
"""


DML_MCP_SERVER_UPDATE_TOOLS_CACHE = """
UPDATE mcp_servers
SET tools_cache = %s
WHERE id = %s AND deleted_at IS NULL
RETURNING id;
"""


DML_AGENT_LIST = """
SELECT a.id, a.name, a.description, a.llm_model_id, a.system_prompt, a.temperature, a.max_tokens, a.memory_strategy, a.memory_window, a.is_active, a.created_by, a.created_at, a.updated_at, lm.display_name AS llm_model_name
FROM agents a
LEFT JOIN llm_models lm ON a.llm_model_id = lm.id
WHERE a.deleted_at IS NULL AND (a.created_by = %s OR %s)
ORDER BY {order_by} {direction}
LIMIT %s OFFSET %s;
"""


DML_AGENT_COUNT = """
SELECT COUNT(*) AS total
FROM agents
WHERE deleted_at IS NULL AND (created_by = %s OR %s);
"""


DML_AGENT_GET_BY_ID = """
SELECT a.id, a.name, a.description, a.llm_model_id, a.system_prompt, a.temperature, a.max_tokens, a.memory_strategy, a.memory_window, a.is_active, a.created_by, a.created_at, a.updated_at, lm.display_name AS llm_model_name
FROM agents a
LEFT JOIN llm_models lm ON a.llm_model_id = lm.id
WHERE a.id = %s AND a.deleted_at IS NULL;
"""


DML_AGENT_GET_BY_NAME_AND_OWNER = """
SELECT id, name, description, llm_model_id, system_prompt, temperature, max_tokens, memory_strategy, memory_window, is_active, created_by, created_at, updated_at
FROM agents
WHERE name = %s AND created_by = %s AND deleted_at IS NULL;
"""


DML_AGENT_CREATE = """
INSERT INTO agents (name, description, llm_model_id, system_prompt, temperature, max_tokens, memory_strategy, memory_window, is_active, created_by)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (name, created_by) WHERE deleted_at IS NULL DO NOTHING
RETURNING id, name, description, llm_model_id, system_prompt, temperature, max_tokens, memory_strategy, memory_window, is_active, created_by, created_at;
"""


DML_AGENT_UPDATE = """
UPDATE agents
SET name = %s, description = %s, llm_model_id = %s, system_prompt = %s, temperature = %s, max_tokens = %s, memory_strategy = %s, memory_window = %s, is_active = %s
WHERE id = %s AND deleted_at IS NULL
RETURNING id, name, description, llm_model_id, system_prompt, temperature, max_tokens, memory_strategy, memory_window, is_active, created_by, updated_at;
"""


DML_AGENT_DELETE = """
UPDATE agents
SET deleted_at = NOW()
WHERE id = ANY(%s) AND deleted_at IS NULL
RETURNING id, name;
"""


DML_AGENT_LIST_ACTIVE = """
SELECT a.id, a.name, a.description, a.llm_model_id, a.system_prompt, a.temperature, a.max_tokens, a.memory_strategy, a.memory_window, a.is_active, a.created_by, a.created_at, a.updated_at, lm.display_name AS llm_model_name
FROM agents a
LEFT JOIN llm_models lm ON a.llm_model_id = lm.id
WHERE a.deleted_at IS NULL AND a.is_active = TRUE
ORDER BY a.created_at DESC;
"""


DML_AGENT_MCP_LIST = """
SELECT ams.id, ams.agent_id, ams.mcp_server_id, ams.allowed_tools, ams.priority, ams.created_at, ms.name AS mcp_server_name
FROM agent_mcp_servers ams
LEFT JOIN mcp_servers ms ON ams.mcp_server_id = ms.id
WHERE ams.agent_id = %s
ORDER BY ams.priority ASC, ams.created_at ASC;
"""


DML_AGENT_MCP_CREATE = """
INSERT INTO agent_mcp_servers (agent_id, mcp_server_id, allowed_tools, priority)
VALUES (%s, %s, %s, %s)
ON CONFLICT (agent_id, mcp_server_id) DO UPDATE SET allowed_tools = EXCLUDED.allowed_tools, priority = EXCLUDED.priority
RETURNING id, agent_id, mcp_server_id, allowed_tools, priority, created_at;
"""


DML_AGENT_MCP_DELETE = """
DELETE FROM agent_mcp_servers
WHERE agent_id = %s AND mcp_server_id = %s
RETURNING id, mcp_server_id;
"""


DML_AGENT_MCP_DELETE_BY_AGENT = """
DELETE FROM agent_mcp_servers
WHERE agent_id = %s
RETURNING id;
"""


DML_AGENT_THREAD_LIST = """
SELECT thread_id, agent_id, user_id, title, agent_snapshot, created_at, updated_at
FROM agent_threads
WHERE agent_id = %s AND deleted_at IS NULL
ORDER BY updated_at DESC
LIMIT %s OFFSET %s;
"""


DML_AGENT_THREAD_COUNT = """
SELECT COUNT(*) AS total
FROM agent_threads
WHERE agent_id = %s AND deleted_at IS NULL;
"""


DML_AGENT_THREAD_GET_BY_ID = """
SELECT thread_id, agent_id, user_id, title, agent_snapshot, created_at, updated_at
FROM agent_threads
WHERE thread_id = %s AND deleted_at IS NULL;
"""


DML_AGENT_THREAD_CREATE = """
INSERT INTO agent_threads (thread_id, agent_id, user_id, title, agent_snapshot)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (thread_id) DO UPDATE SET title = EXCLUDED.title, agent_snapshot = EXCLUDED.agent_snapshot, updated_at = NOW()
RETURNING thread_id, agent_id, user_id, title, agent_snapshot, created_at;
"""


DML_AGENT_THREAD_DELETE = """
UPDATE agent_threads
SET deleted_at = NOW()
WHERE thread_id = %s AND deleted_at IS NULL
RETURNING thread_id;
"""
