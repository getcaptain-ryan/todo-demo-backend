"""SQL queries for Todo entity"""

# Create a new todo
CREATE_TODO = """
    INSERT INTO todos (title, description, completed)
    VALUES ($1, $2, $3)
    RETURNING id, title, description, completed, created_at, updated_at
"""

# Get all todos
GET_ALL_TODOS = """
    SELECT id, title, description, completed, created_at, updated_at
    FROM todos
    ORDER BY created_at DESC
"""

# Get a single todo by ID
GET_TODO_BY_ID = """
    SELECT id, title, description, completed, created_at, updated_at
    FROM todos
    WHERE id = $1
"""

# Update a todo
UPDATE_TODO = """
    UPDATE todos
    SET title = $2, description = $3, completed = $4, updated_at = NOW()
    WHERE id = $1
    RETURNING id, title, description, completed, created_at, updated_at
"""

# Delete a todo
DELETE_TODO = """
    DELETE FROM todos
    WHERE id = $1
    RETURNING id
"""

# Mark todo as completed
MARK_TODO_COMPLETED = """
    UPDATE todos
    SET completed = true, updated_at = NOW()
    WHERE id = $1
    RETURNING id, title, description, completed, created_at, updated_at
"""

# Mark todo as incomplete
MARK_TODO_INCOMPLETE = """
    UPDATE todos
    SET completed = false, updated_at = NOW()
    WHERE id = $1
    RETURNING id, title, description, completed, created_at, updated_at
"""

