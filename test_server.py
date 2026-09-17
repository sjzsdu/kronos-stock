#!/usr/bin/env python3
"""
简单的HTTP服务器来提供测试页面
"""
import http.server
import socketserver
import os
import webbrowser

PORT = 8000
DIRECTORY = "/Users/juzhongsun/Codes/projects/kronos-stock"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

def start_server():
    """启动测试服务器"""
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🌐 测试服务器运行在: http://localhost:{PORT}/")
        print(f"📋 测试页面: http://localhost:{PORT}/test_components.html")
        print("按 Ctrl+C 停止服务器")
        
        # 自动打开浏览器
        webbrowser.open(f'http://localhost:{PORT}/test_components.html')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")

if __name__ == "__main__":
    start_server()