import json
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


@dataclass
class StewardStub:
    status: int = 201
    work_order_id: str = "6f1c1f0e-2f4b-4a55-9d1a-3c1f0e2f4b4a"
    delay_seconds: float = 0.0
    requests: list[tuple[str, dict]] = field(default_factory=list)
    url: str = ""

    def respond(self, handler: BaseHTTPRequestHandler) -> None:
        length = int(handler.headers.get("Content-Length", 0))
        self.requests.append((handler.path, json.loads(handler.rfile.read(length) or b"{}")))
        time.sleep(self.delay_seconds)
        body = json.dumps({"id": self.work_order_id}).encode()
        handler.send_response(self.status)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(body)))
        handler.end_headers()
        handler.wfile.write(body)


@contextmanager
def running_steward_stub() -> Iterator[StewardStub]:
    stub = StewardStub()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            stub.respond(self)

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    stub.url = f"http://127.0.0.1:{server.server_port}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield stub
    finally:
        server.shutdown()
        server.server_close()
