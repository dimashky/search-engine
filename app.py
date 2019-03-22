from flask import Flask, request, render_template, send_from_directory
from searchengine import indexer, matcher, queryspellchecker
import json

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    query = request.args.get('terms')
    results = matcher.match(query)
    suggested_query = queryspellchecker.getSuggestedQuery(query)
    return render_template('results.html', results = results, query = query, suggested_query = suggested_query)

@app.route('/assets/<path:path>')
def sendAsset(path):
    return send_from_directory('static',path)

@app.route('/docs/<path:path>')
def sendDoc(path):
    return send_from_directory('docs',path)

@app.route('/docs')
def getDocs():
    return json.dumps(indexer.getFilesInDir('./docs/'))

@app.route('/index-table')
def indexTable():
    fresh = request.args.get('fresh')
    return render_template('index_table.html', rows = indexer.index(fresh, './docs/'))

if __name__ == '__main__':
    app.run()
