# from flask import Flask, render_template

# app = Flask(__name__)


# @app.route('/')
# def index():
#     return render_template("index.html")


# @app.route('/google80b948fc97355c5a.html')
# def google_verification():
#     return render_template('google80b948fc97355c5a.html')


# if __name__ == '__main__':
#     # 在主线程中运行Flask应用
#     app.run(debug=True, port=5000)

from flask import Flask, request, Response
import requests
import threading
import socket

app = Flask(__name__)

# 获取本机IP地址
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# 代理请求处理
@app.route('/<path:url>', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])
def proxy(url):
    # 目标URL处理
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # 准备请求参数
    headers = dict(request.headers)
    # 移除Flask添加的多余头部
    if 'Host' in headers:
        del headers['Host']
    
    try:
        # 转发请求
        if request.method == 'GET':
            resp = requests.get(url, headers=headers, params=request.args, timeout=30)
        elif request.method == 'POST':
            resp = requests.post(url, headers=headers, params=request.args, 
                               data=request.get_data(), timeout=30)
        elif request.method == 'PUT':
            resp = requests.put(url, headers=headers, params=request.args, 
                              data=request.get_data(), timeout=30)
        elif request.method == 'DELETE':
            resp = requests.delete(url, headers=headers, params=request.args, timeout=30)
        elif request.method == 'HEAD':
            resp = requests.head(url, headers=headers, params=request.args, timeout=30)
        else:
            return "Method not supported", 405
        
        # 准备响应
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                  if name.lower() not in excluded_headers]
        
        return Response(resp.content, resp.status_code, headers)
    
    except Exception as e:
        return f"Proxy Error: {str(e)}", 500

# 启动服务器
def run_server():
    server_ip = get_ip()
    server_port = 5000
    print(f"Flask代理服务器已启动")
    print(f"代理地址: http://{server_ip}:5000")
    print(f"使用示例: http://{server_ip}:5000/https://www.example.com")
    app.run(host='0.0.0.0', port=server_port, threaded=True)

if __name__ == '__main__':
    # 在独立线程中启动，避免阻塞
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        # 保持主线程运行
        while True:
            input("按Enter键停止服务器...\n")
            break
    except KeyboardInterrupt:
        print("服务器已停止")    
