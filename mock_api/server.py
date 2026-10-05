import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HOST = "localhost"
PORT = 8000
DATA_FILE = Path(__file__).parent / "students_api.json"
HTML_DATA_FILE = Path(__file__).parent / "students_scraped.html"


class StudentAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/students":
            self._serve_json()
            return

        if self.path == "/scraped-students":
            self._serve_html()
            return

        self.send_response(404)
        self.end_headers()

    def _serve_json(self) -> None:
        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)

            response = json.dumps(data).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        except (OSError, json.JSONDecodeError):
            self.send_response(500)
            self.end_headers()

    def _serve_html(self) -> None:
        try:
            response = HTML_DATA_FILE.read_bytes()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        except OSError:
            self.send_response(500)
            self.end_headers()


def run_server() -> None:
    server = HTTPServer((HOST, PORT), StudentAPIHandler)

    print(f"Mock API running at http://{HOST}:{PORT}/students")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMock API stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()