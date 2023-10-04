import os
from flask import Flask, flash, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
import re
import json
import requests
from PIL import Image, ImageFont, ImageDraw
#import requests


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
    return '''
    <!doctype html>
    <title>Formula Trout League</title>
    <h1>Formula Trout League Admin Tools</h1> 
    <form id="package_form" action="" method="post">
    
      <div class="panel-body">
          <input type ="submit" name="action" value="logparse">
      </div>
      <div class="panel-body">
          <input type ="submit" name="action" value="GrDesgn">
      </div>

    </form>
    '''
    if request.form['action'] == 'logparse':
        return redirect('logparse')
    elif request.form['action'] == 'GrDesgn':
        return redirect('graphicform')

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

@app.route('/graphicform', methods=['GET', 'POST'])
def graph_form():
    if request.method == 'POST':
        grtitle = request.form['title']
        grlink = str(request.form['result'])
        return redirect(url_for('graph_gen', title=grtitle, result=grlink)) #, title=title, result=result
    return ''' 
    <!doctype html>
    <form method=post enctype=multipart/form-data>
        <label for="title">FUCK:</label>
        <input type="text" name="title"><br><br>
        <label for="result">THIS:</label>
        <input type="text" name="result"><br><br>
        <input type="submit" value="SHIT">
    </form> '''





@app.route('/graphicform/graphicgen/<title>/<result>')
def graph_gen(title, result):

    imgwidth = 400
    imgheight = 300
    raceName = title
    x = 80
    result2 = "http://75.119.157.74:8772/results/download/" + result
    try:
        img_r  = Image.open("back.jpg")
        img = img_r.crop((img_r.width*0.4, img_r.height//4, img_r.width*0.6, img_r.height*0.7))
    except:
        img  = Image.new( mode = "RGB", size = (imgwidth, imgheight), color = (50, 50, 50) )

    logo = Image.open("res/Formula_Trout_League.png")
    #img.show()

    font = ImageFont.truetype("/usr/share/fonts/truetype/arkpandora/AerialBd.ttf", 50)

    Im = ImageDraw.Draw(img)

    drivernames = []
    i = 1

    response = requests.get(result2) 
    driversjson = json.loads(response.text)

    for drivers in driversjson['Result']:
        strI = str(i)
        drivernames.append(strI + ". " + drivers['DriverName'])
        i=i+1

    #print(drivernames)
    font = ImageFont.truetype("/usr/share/fonts/truetype/arkpandora/AerialBd.ttf", 35)

    driver3 = drivernames[:3]
    Im.text((10, 10), raceName ,fill=(255, 255, 255), font=font)
    font = ImageFont.truetype("/usr/share/fonts/truetype/arkpandora/AerialBd.ttf", 30)

    for driver2 in driver3:
        Im.text((20, x), driver2 ,fill=(255, 255, 255), font=font)
        x=x+50

    size = (60,40)
    logo = logo.resize(size)
    img.paste(logo, (320,230), logo)

    #img.show()
    img.save("raceresult.jpg")
    return send_file('raceresult.jpg', mimetype='image/jpg')