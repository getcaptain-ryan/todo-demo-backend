"""SQL queries for Task entity"""

# Create a new task
CREATE_TASK = """
    INSERT INTO tasks (title, description, column_id, "order")
    VALUES ($1, $2, $3, $4)
    RETURNING id, title, description, column_id, "order", created_at
"""

# Get all tasks
GET_ALL_TASKS = """
    SELECT id, title, description, column_id, "order", created_at
    FROM tasks
    ORDER BY column_id ASC, "order" ASC
"""

# Get a single task by ID
GET_TASK_BY_ID = """
    SELECT id, title, description, column_id, "order", created_at
    FROM tasks
    WHERE id = $1
"""

# Get all tasks in a specific column
GET_TASKS_BY_COLUMN = """
    SELECT id, title, description, column_id, "order", created_at
    FROM tasks
    WHERE column_id = $1
    ORDER BY "order" ASC
"""

# Update a task
UPDATE_TASK = """
    UPDATE tasks
    SET title = $2, description = $3, "order" = $4
    WHERE id = $1
    RETURNING id, title, description, column_id, "order", created_at
"""

# Delete a task
DELETE_TASK = """
    DELETE FROM tasks
    WHERE id = $1
    RETURNING id, column_id, "order"
"""

# Shift tasks order up within a column (when inserting)
SHIFT_TASKS_UP_IN_COLUMN = """
    UPDATE tasks
    SET "order" = "order" + 1
    WHERE column_id = $1 AND "order" >= $2
"""

# Shift tasks order down within a column (when deleting)
SHIFT_TASKS_DOWN_IN_COLUMN = """
    UPDATE tasks
    SET "order" = "order" - 1
    WHERE column_id = $1 AND "order" > $2
"""

# Reorder task within same column
REORDER_TASK_IN_COLUMN = """
    WITH current_pos AS (
        SELECT "order" as old_order, column_id FROM tasks WHERE id = $1
    )
    UPDATE tasks
    SET "order" = CASE
        WHEN id = $1 THEN $2
        WHEN $2 < (SELECT old_order FROM current_pos)
            AND "order" >= $2
            AND "order" < (SELECT old_order FROM current_pos)
            THEN "order" + 1
        WHEN $2 > (SELECT old_order FROM current_pos)
            AND "order" <= $2
            AND "order" > (SELECT old_order FROM current_pos)
            THEN "order" - 1
        ELSE "order"
    END
    WHERE column_id = (SELECT column_id FROM current_pos)
        AND "order" BETWEEN
            LEAST($2, (SELECT old_order FROM current_pos))
            AND GREATEST($2, (SELECT old_order FROM current_pos))
    RETURNING id, title, description, column_id, "order", created_at
"""

# Move task to different column
MOVE_TASK_TO_COLUMN = """
    WITH task_info AS (
        SELECT column_id as old_column_id, "order" as old_order
        FROM tasks
        WHERE id = $1
    )
    UPDATE tasks
    SET column_id = $2, "order" = $3
    WHERE id = $1
    RETURNING id, title, description, column_id, "order", created_at
"""

# Get max order in a column
GET_MAX_ORDER_IN_COLUMN = """
    SELECT COALESCE(MAX("order"), -1) as max_order
    FROM tasks
    WHERE column_id = $1
"""

