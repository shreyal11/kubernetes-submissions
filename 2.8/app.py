import os
import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

PORT = int(os.getenv("PORT", "8080"))
TODO_BACKEND_URL = os.getenv(
    "TODO_BACKEND_URL",
    "http://todo-backend-svc:2345"
)


def get_todos():
    try:
        with urllib.request.urlopen(
            f"{TODO_BACKEND_URL}/todos",
            timeout=5
        ) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching todos: {e}", flush=True)
        return []


def create_todo(content):
    data = json.dumps({
        "content": content
    }).encode()

    request = urllib.request.Request(
        f"{TODO_BACKEND_URL}/todos",
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode())


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            return

        todos = get_todos()

        todo_items = "".join(
            f"<li>{todo['content']}</li>"
            for todo in todos
        )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Todo App</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 700px;
                    margin: 50px auto;
                    padding: 20px;
                }}

                h1 {{
                    text-align: center;
                }}

                form {{
                    display: flex;
                    gap: 10px;
                }}

                input {{
                    flex: 1;
                    padding: 10px;
                    font-size: 16px;
                }}

                button {{
                    padding: 10px 20px;
                    font-size: 16px;
                    cursor: pointer;
                }}

                ul {{
                    padding: 0;
                    list-style: none;
                }}

                li {{
                    padding: 12px;
                    margin: 8px 0;
                    background: #f5f5f5;
                    border-left: 4px solid #4caf50;
                }}
            </style>
        </head>

        <body>
            <h1>Todo App</h1>

            <form action="/todos" method="post">
                <input
                    type="text"
                    name="content"
                    maxlength="140"
                    required
                    placeholder="Enter a new todo (max 140 characters)"
                >
                <button type="submit">Send</button>
            </form>

            <h2>Todos</h2>

            <ul>
                {todo_items}
            </ul>

            <p>DevOps with Kubernetes 2026</p>
        </body>
        </html>
        """

        response = html.encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_POST(self):
        if self.path != "/todos":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()

        form = parse_qs(body)
        content = form.get("content", [""])[0].strip()

        if not content or len(content) > 140:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid todo")
            return

        try:
            create_todo(content)

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

        except Exception as e:
            print(f"Error creating todo: {e}", flush=True)

            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Failed to create todo")

    def log_message(self, format, *args):
        return


server = HTTPServer(
    ("0.0.0.0", PORT),
    Handler
)

print(
    f"Todo frontend started in port {PORT}",
    flush=True
)

server.serve_forever()
