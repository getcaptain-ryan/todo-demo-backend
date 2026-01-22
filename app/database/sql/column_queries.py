"""SQL queries for Column entity"""

# Create a new column
CREATE_COLUMN = """
    INSERT INTO columns (title, "order")
    VALUES ($1, $2)
    RETURNING id, title, "order", created_at
"""

# Get all columns
GET_ALL_COLUMNS = """
    SELECT id, title, "order", created_at
    FROM columns
    ORDER BY "order" ASC
"""

# Get a single column by ID
GET_COLUMN_BY_ID = """
    SELECT id, title, "order", created_at
    FROM columns
    WHERE id = $1
"""

# Update a column
UPDATE_COLUMN = """
    UPDATE columns
    SET title = $2, "order" = $3
    WHERE id = $1
    RETURNING id, title, "order", created_at
"""

# Delete a column
DELETE_COLUMN = """
    DELETE FROM columns
    WHERE id = $1
    RETURNING id
"""

# Get max order value
GET_MAX_ORDER = """
    SELECT COALESCE(MAX("order"), -1) as max_order
    FROM columns
"""

# Shift columns order up (when inserting)
SHIFT_COLUMNS_UP = """
    UPDATE columns
    SET "order" = "order" + 1
    WHERE "order" >= $1
"""

# Shift columns order down (when deleting)
SHIFT_COLUMNS_DOWN = """
    UPDATE columns
    SET "order" = "order" - 1
    WHERE "order" > $1
"""

# Reorder column (complex operation)
REORDER_COLUMN = """
    WITH current_pos AS (
        SELECT "order" as old_order FROM columns WHERE id = $1
    )
    UPDATE columns
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
    WHERE "order" BETWEEN 
        LEAST($2, (SELECT old_order FROM current_pos)) 
        AND GREATEST($2, (SELECT old_order FROM current_pos))
    RETURNING id, title, "order", created_at
"""

