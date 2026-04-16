from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

class GameHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/launch':
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', 8080))
                sock.close()
                
                if result == 0:
                    print("C++ game server is running - connection available")
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b"ready")
                else:
                    print("C++ game server not responding")
                    self.send_response(503)
                    self.end_headers()
            except Exception as e:
                print(f"Error: {e}")
                self.send_response(503)
                self.end_headers()
    
    def log_message(self, format, *args):
        pass

server = HTTPServer(('127.0.0.1', 8000), GameHandler)
print("Server running. Checking for C++ game server on port 8080.")
print("Press Ctrl+C to stop.")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
    server.shutdown()
