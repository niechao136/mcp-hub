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
