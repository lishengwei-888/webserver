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



from flask import Flask, request, Response, abort
import requests, socket, select, base64

app = Flask(__name__)

# 用户认证信息（可改为配置或环境变量获取）
USERNAME = 'testuser'
PASSWORD = 'testpass'

def check_auth(auth):
    """检查 Authorization 头中的用户名密码"""
    return auth and auth.username == USERNAME and auth.password == PASSWORD

@app.before_request
def authenticate():
    """统一进行 HTTP Basic 认证"""
    auth = request.authorization
    if not check_auth(auth):
        # 未认证时返回 401，并要求客户端提供认证信息
        return Response(
            '认证失败', 
            401, 
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )

# 捕获所有路径的常见 HTTP 方法请求（不含 CONNECT）
@app.route('/', defaults={'path': ''}, methods=['GET','POST','PUT','DELETE','PATCH','OPTIONS','HEAD'])
@app.route('/<path:path>', methods=['GET','POST','PUT','DELETE','PATCH','OPTIONS','HEAD'])
def proxy(path):
    # 构造目标 URL（Flask 的 request.url 在代理模式下通常已包含完整目标地址）
    target_url = request.url
    # 构造并过滤请求头，去除 Host、Connection 等与代理无关的头部
    headers = {}
    for header, value in request.headers:
        if header.lower() in ['host', 'proxy-authorization', 'connection', 'keep-alive']:
            continue
        headers[header] = value
    # 转发请求到目标服务器
    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            stream=True,
            allow_redirects=False
        )
    except requests.RequestException:
        abort(502)  # 转发失败时返回 Bad Gateway

    # 流式读取目标服务器响应内容并返回给客户端:contentReference[oaicite:2]{index=2}
    def generate():
        for chunk in resp.iter_content(chunk_size=4096):
            if chunk:
                yield chunk
    # 过滤掉“分块编码”、“长度”等头，由 Flask 自动处理响应
    excluded = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    response_headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded]
    return Response(generate(), status=resp.status_code, headers=response_headers)

if __name__ == '__main__':
    # Flask 内置服务器，生产环境建议使用 Gunicorn 等 WSGI 服务器
    app.run(host='0.0.0.0', port=8888)
