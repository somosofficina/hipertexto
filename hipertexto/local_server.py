from http.server import SimpleHTTPRequestHandler
from pathlib import Path


class CleanURLHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if Path('.' + self.path).is_file():
            return super().do_GET()

        html_path = self.path.rstrip('/') + '.html'
        if Path('.' + html_path).is_file():
            self.path = html_path
            return super().do_GET()

        return super().do_GET()
