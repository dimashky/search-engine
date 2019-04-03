from flask import Flask, request, render_template, send_from_directory, flash, redirect, url_for
from searchengine import indexer, matcher, queryspellchecker, tester, loader
import json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = './docs/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'HelloSearchEngine'
app.config['SESSION_TYPE'] = 'filesystem'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search')
def search():
    query = request.args.get('terms')
    results = matcher.match(query)
    suggested_query = queryspellchecker.getSuggestedQuery(query)
    return render_template('results.html', results=results, query=query, suggested_query=suggested_query)


@app.route('/assets/<path:path>')
def sendAsset(path):
    return send_from_directory('static', path)


@app.route('/docs/<path:path>')
def sendDoc(path):
    return send_from_directory('docs', path)


@app.route('/docs')
def getDocs():
    return render_template('corpus.html', results=loader.getFilesInDir('./docs/', True, 500))


@app.route('/index-table')
def indexTable():
    fresh = request.args.get('fresh')
    return render_template('index_table.html', rows=indexer.index(fresh, './docs/'))


@app.route('/bigram_index')
def bigramIndex():
    return render_template('index_table.html', rows=indexer.bigramIndex())


@app.route('/soundex_index')
def soundexIndex():
    return render_template('index_table.html', rows=indexer.soundexIndex())


@app.route('/test_cases')
def testCases():
    fresh = request.args.get('fresh')
    return render_template('test_cases.html', rows=tester.test(fresh))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'files' not in request.files:
            print('No file part')
            return redirect(request.url)
        files = request.files.getlist("files")
        files_name = []
        for file in files:
            print
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                print('No selected file')
                return redirect('/docs')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                files_name.append(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        indexer.index(True, app.config['UPLOAD_FOLDER'], files_name)
    return redirect('/docs')

if __name__ == '__main__':
    app.run()
