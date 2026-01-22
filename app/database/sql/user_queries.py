"""SQL queries for User entity"""

# Create a new user
CREATE_USER = """
    INSERT INTO users (name, email, avatar_url)
    VALUES ($1, $2, $3)
    RETURNING id, name, email, avatar_url, created_at
"""

# Get all users
GET_ALL_USERS = """
    SELECT id, name, email, avatar_url, created_at
    FROM users
    ORDER BY created_at DESC
"""

# Get a single user by ID
GET_USER_BY_ID = """
    SELECT id, name, email, avatar_url, created_at
    FROM users
    WHERE id = $1
"""

# Get a user by email
GET_USER_BY_EMAIL = """
    SELECT id, name, email, avatar_url, created_at
    FROM users
    WHERE email = $1
"""

# Update a user
UPDATE_USER = """
    UPDATE users
    SET name = $2, email = $3, avatar_url = $4
    WHERE id = $1
    RETURNING id, name, email, avatar_url, created_at
"""

# Delete a user
DELETE_USER = """
    DELETE FROM users
    WHERE id = $1
    RETURNING id
"""

