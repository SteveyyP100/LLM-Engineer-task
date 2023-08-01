import os
import pandas as pd
from fileinput import filename
from distutils.log import debug
from werkzeug.utils import secure_filename
from utils import gpt_conversation, gpt_step_by_step
from flask import Flask, request, render_template, session

app = Flask(__name__)

# ChatGPT Message History
message_history = []

# Setup folders for uploading csv files
BASE_PATH = 'app'
UPLOAD_FOLDER = os.path.join(BASE_PATH, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = open('secretkey.txt', 'r').read().strip('\n')

@app.route('/', methods=["GET", "POST"])
def main():
    if request.method == 'POST':
      # upload file flask
        f = request.files.get('file')
 
        # Extracting uploaded file name
        data_filename = secure_filename(f.filename)
 
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
 
        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
 
        return render_template('index_uploaded.html')
    return render_template("index.html")


@app.route('/one-shot-predict', methods=["GET", "POST"])
def one_shot_predict():

    #Columns
    columns = request.form.to_dict()

    # Uploaded File Path
    data_file_path = session.get('uploaded_data_file_path', None)

    # Read CSV
    df = pd.read_csv(data_file_path, encoding='unicode_escape')
    
    if columns == '':
        return {"error": f"Invalid columns data: {columns}"}

    message_history, response = gpt_conversation(df=df, columns=columns)
    table = response[response.find('<table>'):(response.find('</table>')+8)]

    return render_template("response.html", table=table)


@app.route('/step-by-step-predict', methods=["GET", "POST"])
def step_by_step_predict():

    # Data
    global message_history
    body = request.form.to_dict()
    user_message = body.get('user-message')

    # Check Users Submission
    if user_message:
        message_history.append({'role': 'user', 'content': user_message})

    # Uploaded File Path
    data_file_path = session.get('uploaded_data_file_path', None)

    # Read CSV
    df = pd.read_csv(data_file_path, encoding='unicode_escape')

    message_history = gpt_step_by_step(message_history=message_history, df=df)

    return render_template("message_history.html", data=message_history)



if __name__ == "__main__":
    app.run(debug=True)