from pathlib import Path
from threading import Thread
from http.server import HTTPServer, SimpleHTTPRequestHandler

from app.sources.web_scraper import extract_web_table


def test_scraper_reads_html_table(tmp_path):
    html = """
    <html><body>
    <table id="students">
        <thead><tr><th>Student ID</th><th>City</th></tr></thead>
        <tbody>
            <tr><td>1001</td><td>Sanaa</td></tr>
            <tr><td>1002</td><td>Aden</td></tr>
            <tr><td>1002</td><td>Aden</td></tr>
        </tbody>
    </table>
    </body></html>
    """
    page = tmp_path / "students.html"
    page.write_text(html, encoding="utf-8")

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    import os

    old_cwd = Path.cwd()
    server = None
    try:
        os.chdir(tmp_path)
        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()

        data = extract_web_table(
            f"http://127.0.0.1:{server.server_port}/students.html",
            table_selector="#students",
            row_selector="tbody tr",
            header_selector="thead th",
            cell_selector="td",
        )
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        os.chdir(old_cwd)

    assert len(data) == 2
    assert list(data["student_id"]) == [1001, 1002]
    assert data.loc[data["student_id"] == 1001, "city"].iloc[0] == "Sanaa"


def test_scraper_failure_returns_empty_dataframe():
    data = extract_web_table("http://127.0.0.1:1/not-found")
    assert data.empty
