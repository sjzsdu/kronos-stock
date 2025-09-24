#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import create_app
from flask import Flask
import webbrowser
import threading
import time

def start_app():
    """Start the Flask app for testing"""
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5555, use_reloader=False)

def test_in_browser():
    """Open browser to test the modal"""
    # Wait for server to start
    time.sleep(2)
    
    # Open the main page
    url = "http://127.0.0.1:5555/history"
    print(f"Opening {url} in browser...")
    print("请在浏览器中:")
    print("1. 打开预测历史页面")
    print("2. 点击任意一个预测记录的详情按钮")
    print("3. 查看是否能看到图表数据")
    print("4. 按 Ctrl+C 停止测试服务器")
    
    webbrowser.open(url)

if __name__ == '__main__':
    # Start the browser test in a separate thread
    browser_thread = threading.Thread(target=test_in_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the Flask app (this will block)
    try:
        start_app()
    except KeyboardInterrupt:
        print("\n测试服务器已停止")