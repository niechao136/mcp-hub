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
