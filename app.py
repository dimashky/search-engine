from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    results = request.args.get('terms').split()
    return render_template('results.html', results = results, query = request.args.get('terms'))

@app.route('/assets/<path:path>')
def send_asset(path):
    return send_from_directory('static',path)

if __name__ == '__main__':
    app.run()
