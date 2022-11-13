import os
from flask import Flask, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import re

#Flask file config
UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = {'log'}

app = Flask(__name__)

app.config['SECRET_KEY'] = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Trout defined
DRSpen = "TROUT_DRS: Penalty"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        return redirect('logparse')
    return '''
    <!doctype html>
    <title>Formula Trout League</title>
    <h1>Formula Trout League Admin Tools</h1>
    <form method=post enctype=multipart/form-data>
      <input type=submit value=Log_analyzer>
    '''

@app.route('/logparse', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('process_file', name=filename))

    return '''
    <!doctype html>
    <title>Formula Trout League</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/logparse/res/<name>')
def process_file(name):
    lines=[]
    Pens=[]
    with open (name) as f:
        for line in f:
            if "Name: Practice" in line:
                session = "P"
            elif "Name: Qualifying 1" in line:
                session = "Q1"
            elif "Name: Qualifying 2" in line:
                session = "Q2"
            elif "Name: Qualify" in line:
                session = "Q"
            elif "Name: Warm Up" in line:
                session = "W"
            elif "Name: Race" in line:
                session = "R"
            elif "TROUT_DRS: Penalty" in line:
                drvCheck = re.search('\((.*)\)', line)
                drvName = str(drvCheck.group(1))
                penCheck = re.search('\,(.*)\"', line)
                penName = str(penCheck.group(1))
                Pens.append(drvName + penName + session)
        return Pens
    return "EOP"
