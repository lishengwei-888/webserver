from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/google80b948fc97355c5a.html')
def google_verification():
    return render_template('google80b948fc97355c5a.html')


if __name__ == '__main__':
    # 在主线程中运行Flask应用
    app.run(debug=True, port=5000)
