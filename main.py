import os
from flask import Flask, render_template, jsonify, flash, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
import re
import json
import requests
from PIL import Image, ImageFont, ImageDraw
#import requests

from forms import LogParseForm, GraphicGeneratorForm

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
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/logparse', methods=['GET', 'POST'])
def upload_file():
    form = LogParseForm()
    if request.method == 'POST':
        file = form.file_name.data

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

    if request.method == 'GET':
        return render_template('logparse.html', form=form)

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

@app.route('/graphicform', methods=['GET', 'POST'])
def graph_form():
    form = GraphicGeneratorForm()
    if request.method == 'POST':
        grtitle = request.form['race_title']
        grlink = str(request.form['json_file_name'])
        return redirect(url_for('graph_gen', title=grtitle, event=grlink)) #, title=title, result=result

    if request.method == 'GET':
        return render_template('graphicform.html', form=form)

@app.route('/graphicform/graphicgen/<title>/<event>')
def graph_gen(title, event):
    url = "http://75.119.157.74:8772/results/download/" + event
    response = requests.get(url) 
    if response.status_code == 404:
        return f'The race results from the URL {url} could not be downloaded.'
    
    drivers_json = response.json()

    imgwidth = 400
    imgheight = 300
    raceName = title
    x = 80
    
    try:
        img_r  = Image.open("back.jpg")
        img = img_r.crop((img_r.width*0.4, img_r.height//4, img_r.width*0.6, img_r.height*0.7))
    except:
        img  = Image.new( mode = "RGB", size = (imgwidth, imgheight), color = (50, 50, 50) )

    logo = Image.open("res/Formula_Trout_League_logo.png")
    #img.show()

    # font = ImageFont.truetype("./res/fonts/ArialBd.ttf", 50)

    Im = ImageDraw.Draw(img)

    drivernames = []
    i = 1

    for drivers in drivers_json['Result']:
        strI = str(i)
        drivernames.append(strI + ". " + drivers['DriverName'])
        i=i+1

    #print(drivernames)
    font = ImageFont.truetype("./res/fonts/ArialBd.ttf", 35)

    driver3 = drivernames[:3]
    Im.text((10, 10), raceName, fill=(255, 255, 255), font=font)
    font = ImageFont.truetype("./res/fonts/ArialBd.ttf", 30)

    for driver2 in driver3:
        Im.text((20, x), driver2, fill=(255, 255, 255), font=font)
        x=x+50

    size = (60,40)
    logo = logo.resize(size)
    img.paste(logo, (320,230), logo)

    #img.show()
    img.save("./output/raceresult.jpg")
    return send_file('./output/raceresult.jpg', mimetype='image/jpg')

app.run(debug=True)
