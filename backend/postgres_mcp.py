# import asyncio
# import logging
# import os
# import sys
# import traceback
# from dotenv import load_dotenv
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from fastmcp import FastMCP

# # Setup logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("postgres_mcp.log"),
#         logging.StreamHandler(sys.stderr)
#     ]
# )
# logger = logging.getLogger("PostgresMCP")

# # Load environment variables
# load_dotenv()

# # PostgreSQL configuration
# DB_CONFIG = {
#     "dbname": os.getenv("DB_NAME"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "host": os.getenv("DB_HOST", "localhost"),
#     "port": os.getenv("DB_PORT", "5432"),
# }

# def get_db_connection():
#     try:
#         return psycopg2.connect(**DB_CONFIG)
#     except psycopg2.Error as e:
#         logger.error(f"Failed to connect to database: {str(e)}")
#         raise

# # Test database connection and create tasks table if it doesn't exist
# def test_db_connection():
#     try:
#         with get_db_connection() as conn:
#             with conn.cursor() as cur:
#                 # Check if tasks table exists, create if it doesn't
#                 cur.execute("""
#                     SELECT EXISTS (
#                         SELECT FROM information_schema.tables 
#                         WHERE table_name = 'tasks'
#                     );
#                 """)
#                 if not cur.fetchone()[0]:
#                     logger.info("Creating tasks table...")
#                     cur.execute("""
#                         CREATE TABLE tasks (
#                             id SERIAL PRIMARY KEY,
#                             task_name VARCHAR(255) NOT NULL,
#                             description TEXT,
#                             github_issue_id INTEGER,
#                             github_issue_url VARCHAR(255),
#                             status VARCHAR(50) CHECK (status IN ('open', 'notplanned', 'completed')),
#                             original_status VARCHAR(50) CHECK (original_status IN ('open', 'notplanned', 'completed')),
#                             priority VARCHAR(50) CHECK (priority IN ('low', 'medium', 'high')),
#                             assignee VARCHAR(100),
#                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#                         )
#                     """)
#                     conn.commit()
#                     logger.info("Tasks table created successfully")
#             logger.info("Database connection successful")
#             return True
#     except psycopg2.Error as e:
#         logger.error(f"Database connection failed: {str(e)}")
#         return False

# # Initialize MCP server
# app = FastMCP(server_name="PostgresMCP")

# # Tool: insert_task
# @app.tool(name="insert_task")
# async def insert_task(task_name: str, description: str, github_issue_id: int, github_issue_url: str, status: str = "open", priority: str = "low", assignee: str | None = None) -> dict:
#     logger.info(f"Inserting task: {task_name}")
#     try:
#         with get_db_connection() as conn:
#             with conn.cursor(cursor_factory=RealDictCursor) as cur:
#                 cur.execute(
#                     """
#                     INSERT INTO tasks (task_name, description, github_issue_id, github_issue_url, status, original_status, priority, assignee)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                     RETURNING id
#                     """,
#                     (task_name, description, github_issue_id, github_issue_url, status, status, priority, assignee)
#                 )
#                 task_id = cur.fetchone()["id"]
#                 conn.commit()
#                 logger.info(f"Task inserted with ID: {task_id}")
#                 return {"task_id": task_id, "task_name": task_name}
#     except Exception as e:
#         logger.error(f"Failed to insert task: {str(e)}")
#         raise

# # Tool: get_tasks
# @app.tool(name="get_tasks")
# async def get_tasks(status: str | None = None, priority: str | None = None, assignee: str | None = None) -> list:
#     logger.info("Retrieving tasks with filters")
#     try:
#         with get_db_connection() as conn:
#             with conn.cursor(cursor_factory=RealDictCursor) as cur:
#                 query = "SELECT * FROM tasks WHERE 1=1"
#                 params = []
                
#                 if status:
#                     query += " AND status = %s"
#                     params.append(status)
#                 if priority:
#                     query += " AND priority = %s"
#                     params.append(priority)
#                 if assignee:
#                     query += " AND assignee = %s"
#                     params.append(assignee)
                    
#                 query += " ORDER BY id"
                
#                 cur.execute(query, params)
#                 rows = cur.fetchall()
#                 logger.info(f"Retrieved {len(rows)} tasks")
#                 for row in rows:
#                     for k, v in row.items():
#                         if not isinstance(v, (str, int, float, bool, type(None))):
#                             row[k] = str(v)
#                 return rows
#     except Exception as e:
#         logger.error(f"Failed to retrieve tasks: {str(e)}")
#         raise

# # Tool: update_task_status
# @app.tool(name="update_task_status")
# async def update_task_status(github_issue_id: int, status: str) -> dict:
#     logger.info(f"Processing task for GitHub issue ID: {github_issue_id} with new_status: {status}")
    
#     if status not in ["open", "notplanned", "completed"]:
#         logger.error(f"Invalid status value: {status}")
#         return {"status": "error", "message": f"Invalid status: {status}"}
    
#     try:
#         with get_db_connection() as conn:
#             with conn.cursor(cursor_factory=RealDictCursor) as cur:
#                 # Check if the task exists and get current status
#                 cur.execute(
#                     "SELECT id, task_name, status, original_status FROM tasks WHERE github_issue_id = %s",
#                     (github_issue_id,)
#                 )
#                 task = cur.fetchone()
#                 if not task:
#                     logger.warning(f"No task found with GitHub issue ID: {github_issue_id}")
#                     return {"status": "error", "message": "Task not found"}

#                 # Skip update if status hasn't changed
#                 if task["status"] == status:
#                     logger.info(f"Task {github_issue_id} already has status {status}, skipping update")
#                     return {"status": "success", "task": task, "message": "Status unchanged"}

#                 # Update the task's status and updated_at timestamp
#                 cur.execute(
#                     """
#                     UPDATE tasks 
#                     SET status = %s, updated_at = CURRENT_TIMESTAMP
#                     WHERE github_issue_id = %s
#                     RETURNING id, task_name, status, original_status
#                     """,
#                     (status, github_issue_id)
#                 )
#                 updated_task = cur.fetchone()
#                 conn.commit()  # Explicitly commit the transaction
#                 logger.info(f"Task updated successfully: {updated_task}")
#                 return {"status": "success", "task": updated_task, "message": f"Status updated to {status}"}
                
#     except psycopg2.Error as e:
#         logger.error(f"Database error while updating task: {str(e)}", exc_info=True)
#         return {"status": "error", "message": f"Database error: {str(e)}"}
#     except Exception as e:
#         logger.error(f"Unexpected error while updating task: {str(e)}", exc_info=True)
#         return {"status": "error", "message": f"Unexpected error: {str(e)}"}

# # Function to start the server (will be called from main.py)
# async def start_server():
#     logger.info("Starting Postgres MCP server on TCP port 9001...")
#     try:
#         if not test_db_connection():
#             logger.error("Cannot start Postgres MCP server: Database connection failed")
#             return None
        
#         async def handle_connection(reader, writer):
#             try:
#                 await app.run(connection=(reader, writer))
#             except Exception as e:
#                 logger.error(f"Error handling connection: {str(e)}")
#                 logger.error(traceback.format_exc())
#             finally:
#                 try:
#                     writer.close()
#                     await writer.wait_closed()
#                 except Exception as e:
#                     logger.error(f"Error closing writer: {str(e)}")
            
#         server = await asyncio.start_server(
#             handle_connection,
#             '127.0.0.1',
#             9001
#         )
#         logger.info("Postgres MCP TCP server started")
#         return server
#     except Exception as e:
#         logger.error(f"Postgres MCP server error: {str(e)}", exc_info=True)
#         return None

# # If run directly, start the server
# if __name__ == "__main__":
#     try:
#         asyncio.run(start_server())
#     except KeyboardInterrupt:
#         logger.info("Postgres MCP server stopped by user")
#         sys.exit(0)
#     except Exception as e:
#         logger.error(f"Postgres MCP server critical error: {str(e)}", exc_info=True)
#         sys.exit(1)

import asyncio
import logging
import os
import sys
import traceback
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from fastmcp import FastMCP

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("postgres_mcp.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("PostgresMCP")

# Load environment variables
load_dotenv()

# PostgreSQL configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

# Test database connection and create tasks table if it doesn't exist
def test_db_connection():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if tasks table exists, create if it doesn't
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'tasks'
                    );
                """)
                if not cur.fetchone()[0]:
                    logger.info("Creating tasks table...")
                    cur.execute("""
                        CREATE TABLE tasks (
                            id SERIAL PRIMARY KEY,
                            task_name VARCHAR(255) NOT NULL,
                            description TEXT,
                            github_issue_id INTEGER,
                            github_issue_url VARCHAR(255),
                            status VARCHAR(50) CHECK (status IN ('open', 'notplanned', 'completed')),
                            original_status VARCHAR(50) CHECK (original_status IN ('open', 'notplanned', 'completed')),
                            priority VARCHAR(50) CHECK (priority IN ('low', 'medium', 'high')),
                            assignee VARCHAR(100),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            meeting_description TEXT,
                            assignee_for_meeting TEXT,
                            meeting_datetime TIMESTAMP
                        )
                    """)
                    conn.commit()
                    logger.info("Tasks table created successfully")
                else:
                    # Ensure new columns exist
                    cur.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'tasks';
                    """)
                    columns = [row[0] for row in cur.fetchall()]
                    if 'meeting_description' not in columns:
                        cur.execute("ALTER TABLE tasks ADD COLUMN meeting_description TEXT;")
                    if 'assignee_for_meeting' not in columns:
                        cur.execute("ALTER TABLE tasks ADD COLUMN assignee_for_meeting TEXT;")
                    if 'meeting_datetime' not in columns:
                        cur.execute("ALTER TABLE tasks ADD COLUMN meeting_datetime TIMESTAMP;")
                    conn.commit()
            logger.info("Database connection successful")
            return True
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

# Initialize MCP server
app = FastMCP(server_name="PostgresMCP")

# Tool: insert_task
@app.tool(name="insert_task")
async def insert_task(
    task_name: str,
    description: str,
    github_issue_id: int,
    github_issue_url: str,
    status: str = "open",
    priority: str = "low",
    assignee: str | None = None,
    meeting_description: str | None = None,
    assignee_for_meeting: str | None = None,
    meeting_datetime: str | None = None
) -> dict:
    logger.info(f"Inserting task: {task_name}")
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO tasks (
                        task_name, description, github_issue_id, github_issue_url, 
                        status, original_status, priority, assignee, 
                        meeting_description, assignee_for_meeting, meeting_datetime
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        task_name, description, github_issue_id, github_issue_url,
                        status, status, priority, assignee,
                        meeting_description, assignee_for_meeting, meeting_datetime
                    )
                )
                task_id = cur.fetchone()["id"]
                conn.commit()
                logger.info(f"Task inserted with ID: {task_id}")
                return {"task_id": task_id, "task_name": task_name}
    except Exception as e:
        logger.error(f"Failed to insert task: {str(e)}")
        raise

# Tool: get_tasks
@app.tool(name="get_tasks")
async def get_tasks(status: str | None = None, priority: str | None = None, assignee: str | None = None) -> list:
    logger.info("Retrieving tasks with filters")
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM tasks WHERE 1=1"
                params = []
                
                if status:
                    query += " AND status = %s"
                    params.append(status)
                if priority:
                    query += " AND priority = %s"
                    params.append(priority)
                if assignee:
                    query += " AND assignee = %s"
                    params.append(assignee)
                    
                query += " ORDER BY id"
                
                cur.execute(query, params)
                rows = cur.fetchall()
                logger.info(f"Retrieved {len(rows)} tasks")
                for row in rows:
                    for k, v in row.items():
                        if not isinstance(v, (str, int, float, bool, type(None))):
                            row[k] = str(v)
                return rows
    except Exception as e:
        logger.error(f"Failed to retrieve tasks: {str(e)}")
        raise

# Tool: update_task_status
@app.tool(name="update_task_status")
async def update_task_status(github_issue_id: int, status: str) -> dict:
    logger.info(f"Processing task for GitHub issue ID: {github_issue_id} with new_status: {status}")
    
    if status not in ["open", "notplanned", "completed"]:
        logger.error(f"Invalid status value: {status}")
        return {"status": "error", "message": f"Invalid status: {status}"}
    
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, task_name, status, original_status FROM tasks WHERE github_issue_id = %s",
                    (github_issue_id,)
                )
                task = cur.fetchone()
                if not task:
                    logger.warning(f"No task found with GitHub issue ID: {github_issue_id}")
                    return {"status": "error", "message": "Task not found"}

                if task["status"] == status:
                    logger.info(f"Task {github_issue_id} already has status {status}, skipping update")
                    return {"status": "success", "task": task, "message": "Status unchanged"}

                cur.execute(
                    """
                    UPDATE tasks 
                    SET status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE github_issue_id = %s
                    RETURNING id, task_name, status, original_status
                    """,
                    (status, github_issue_id)
                )
                updated_task = cur.fetchone()
                conn.commit()
                logger.info(f"Task updated successfully: {updated_task}")
                return {"status": "success", "task": updated_task, "message": f"Status updated to {status}"}
                
    except psycopg2.Error as e:
        logger.error(f"Database error while updating task: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Database error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error while updating task: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}

# Function to start the server (will be called from main.py)
async def start_server():
    logger.info("Starting Postgres MCP server on TCP port 9001...")
    try:
        if not test_db_connection():
            logger.error("Cannot start Postgres MCP server: Database connection failed")
            return None
        
        async def handle_connection(reader, writer):
            try:
                await app.run(connection=(reader, writer))
            except Exception as e:
                logger.error(f"Error handling connection: {str(e)}")
                logger.error(traceback.format_exc())
            finally:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception as e:
                    logger.error(f"Error closing writer: {str(e)}")
            
        server = await asyncio.start_server(
            handle_connection,
            '127.0.0.1',
            9001
        )
        logger.info("Postgres MCP TCP server started")
        return server
    except Exception as e:
        logger.error(f"Postgres MCP server error: {str(e)}", exc_info=True)
        return None

# If run directly, start the server
if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Postgres MCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Postgres MCP server critical error: {str(e)}", exc_info=True)
        sys.exit(1)