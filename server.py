#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-YKS Yerlestirme Verisi - basit yerel sunucu (gzip destekli, harici bagimlilik yok)."""
import gzip, io, os, sys, mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get('PORT', '8787'))

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/':
            path = '/index.html'
        fp = os.path.normpath(os.path.join(ROOT, path.lstrip('/')))
        # Paylasilabilir bolum adresleri (/hemsirelik): uzantisiz ve dosyaya
        # karsilik gelmeyen yollar index.html'e duser. Vercel'deki rewrite
        # kuralinin yerel karsiligi; yonlendirme index.html icinde cozuluyor.
        if not os.path.isfile(fp) and '.' not in os.path.basename(path):
            fp = os.path.join(ROOT, 'index.html')
        if not fp.startswith(ROOT) or not os.path.isfile(fp):
            self.send_error(404, "Bulunamadi")
            return
        data = open(fp, 'rb').read()
        ctype = mimetypes.guess_type(fp)[0] or 'application/octet-stream'
        if ctype.startswith('text/') or ctype in ('application/javascript', 'application/json'):
            ctype += '; charset=utf-8'
        headers = [('Content-Type', ctype), ('Cache-Control', 'no-cache')]
        if 'gzip' in self.headers.get('Accept-Encoding', '') and len(data) > 2048:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6) as g:
                g.write(data)
            data = buf.getvalue()
            headers.append(('Content-Encoding', 'gzip'))
        self.send_response(200)
        for k, v in headers:
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == '__main__':
    srv = HTTPServer(('127.0.0.1', PORT), H)
    print(f"\n  2026-YKS Yerlestirme Verisi\n  ->  http://localhost:{PORT}\n  (durdurmak icin Ctrl+C)\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  kapatildi.")
