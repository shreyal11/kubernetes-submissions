import os
import urllib.request
import json

TODO_BACKEND_URL = os.getenv(
    "TODO_BACKEND_URL",
    "http://todo-backend-svc:2345"
)

WIKIPEDIA_RANDOM_URL = "https://en.wikipedia.org/wiki/Special:Random"


def get_random_wikipedia_url():
    request = urllib.request.Request(
        WIKIPEDIA_RANDOM_URL,
        method="GET",
        headers={"User-Agent": "todo-cron/2.9"}
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return response.geturl()


def create_todo(url):
    data = json.dumps({
        "content": f"Read {url}"
    }).encode()

    request = urllib.request.Request(
        f"{TODO_BACKEND_URL}/todos",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        result = response.read().decode()
        print(f"Created todo: {result}", flush=True)


if __name__ == "__main__":
    url = get_random_wikipedia_url()
    print(f"Random Wikipedia article: {url}", flush=True)
    create_todo(url)
