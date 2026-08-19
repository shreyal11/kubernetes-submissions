from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import psycopg2


DB_HOST = os.getenv("DB_HOST", "todo-postgres-svc")
DB_NAME = os.getenv("DB_NAME", "todos")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL
        )
        """
    )

    conn.commit()
    cur.close()
    conn.close()


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/todos":
            try:
                conn = get_connection()
                cur = conn.cursor()

                cur.execute(
                    "SELECT id, content FROM todos ORDER BY id"
                )

                rows = cur.fetchall()

                todos = [
                    {
                        "id": row[0],
                        "content": row[1],
                    }
                    for row in rows
                ]

                cur.close()
                conn.close()

                response = json.dumps(todos).encode()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header(
                    "Content-Length",
                    str(len(response))
                )
                self.end_headers()
                self.wfile.write(response)

            except Exception as e:
                print(f"Database error: {e}", flush=True)
                self.send_response(500)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/todos":
            try:
                length = int(
                    self.headers.get("Content-Length", 0)
                )

                data = json.loads(
                    self.rfile.read(length)
                )

                content = data.get(
                    "content",
                    ""
                ).strip()

                if not content or len(content) > 140:
                    self.send_response(400)
                    self.end_headers()
                    return

                conn = get_connection()
                cur = conn.cursor()

                cur.execute(
                    """
                    INSERT INTO todos (content)
                    VALUES (%s)
                    RETURNING id, content
                    """,
                    (content,),
                )

                row = cur.fetchone()

                conn.commit()

                cur.close()
                conn.close()

                todo = {
                    "id": row[0],
                    "content": row[1],
                }

                response = json.dumps(todo).encode()

                self.send_response(201)
                self.send_header(
                    "Content-Type",
                    "application/json"
                )
                self.send_header(
                    "Content-Length",
                    str(len(response))
                )
                self.end_headers()
                self.wfile.write(response)

            except Exception as e:
                print(f"Database error: {e}", flush=True)
                self.send_response(400)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


init_db()

server = HTTPServer(
    ("0.0.0.0", 8080),
    Handler
)

print(
    "Todo backend started in port 8080",
    flush=True
)

server.serve_forever()
