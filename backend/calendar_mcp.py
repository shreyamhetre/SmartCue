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
        logging.FileHandler("calendar_mcp.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("CalendarMCP")

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

# Test database connection
def test_db_connection():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                logger.info("Database connection successful")
                return True
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

# Initialize MCP server
app = FastMCP(server_name="CalendarMCP")

# Tool: update_meeting
@app.tool(name="update_meeting")
async def update_meeting(
    task_id: int,
    meeting_description: str,
    assignee_for_meeting: str,
    meeting_datetime: str
) -> dict:
    logger.info(f"Updating meeting for task ID: {task_id}")
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    UPDATE tasks
                    SET meeting_description = %s,
                        assignee_for_meeting = %s,
                        meeting_datetime = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, meeting_description, assignee_for_meeting, meeting_datetime
                    """,
                    (meeting_description, assignee_for_meeting, meeting_datetime, task_id)
                )
                result = cur.fetchone()
                if not result:
                    logger.warning(f"No task found with ID: {task_id}")
                    return {"status": "error", "message": "Task not found"}
                conn.commit()
                logger.info(f"Meeting updated for task ID: {task_id}")
                return {"status": "success", "task": result}
    except Exception as e:
        logger.error(f"Failed to update meeting: {str(e)}")
        raise

# Tool: get_meetings
@app.tool(name="get_meetings")
async def get_meetings(start_date: str | None = None, end_date: str | None = None) -> list:
    logger.info("Retrieving meetings with filters")
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT id, task_name, meeting_description, assignee_for_meeting, meeting_datetime
                    FROM tasks
                    WHERE meeting_datetime IS NOT NULL
                """
                params = []
                
                if start_date:
                    query += " AND meeting_datetime >= %s"
                    params.append(start_date)
                if end_date:
                    query += " AND meeting_datetime <= %s"
                    params.append(end_date)
                    
                query += " ORDER BY meeting_datetime"
                
                cur.execute(query, params)
                rows = cur.fetchall()
                logger.info(f"Retrieved {len(rows)} meetings")
                for row in rows:
                    for k, v in row.items():
                        if not isinstance(v, (str, int, float, bool, type(None))):
                            row[k] = str(v)
                return rows
    except Exception as e:
        logger.error(f"Failed to retrieve meetings: {str(e)}")
        raise

# Function to start the server (will be called from main.py)
async def start_server():
    logger.info("Starting Calendar MCP server on TCP port 9002...")
    try:
        if not test_db_connection():
            logger.error("Cannot start Calendar MCP server: Database connection failed")
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
            9002
        )
        logger.info("Calendar MCP TCP server started")
        return server
    except Exception as e:
        logger.error(f"Calendar MCP server error: {str(e)}", exc_info=True)
        return None

# If run directly, start the server
if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Calendar MCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Calendar MCP server critical error: {str(e)}", exc_info=True)
        sys.exit(1)