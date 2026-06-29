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
