from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from typing import override


class CleanURLHandler(SimpleHTTPRequestHandler):
    @override
    def do_GET(self):
        if Path('.' + self.path).is_file():
            return super().do_GET()

        html_path = self.path.rstrip('/') + '.html'
        if Path('.' + html_path).is_file():
            self.path = html_path
            return super().do_GET()

        return super().do_GET()
