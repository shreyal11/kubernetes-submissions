from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import psycopg2

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "pingpong")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/pingpong":
            try:
                conn = get_connection()
                cur = conn.cursor()

                cur.execute(
                    "UPDATE pongs SET count = count + 1 WHERE id = 1 "
                    "RETURNING count;"
                )
                count = cur.fetchone()[0]

                conn.commit()
                cur.close()
                conn.close()

                response = f"pong {count}\n"

                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(response.encode())

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Database error: {e}\n".encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


server = HTTPServer(("0.0.0.0", 8000), Handler)
print("Ping-pong server started in port 8000", flush=True)
server.serve_forever()
