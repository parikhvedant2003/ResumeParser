import os
import ast
import logging
from resume_detector import main
from resume_parser import resumeParser
from logging.handlers import RotatingFileHandler
from flask import Flask, request, has_request_context, render_template

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None
        return super().format(record)

log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

logger = logging.getLogger()
log_file = os.path.join(log_folder, 'resume_parser.log')

formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s\n' 
)

logger = logging.getLogger()

fileHandler = RotatingFileHandler(filename = log_file, maxBytes= 50 * 1048576, backupCount = 10)
fileHandler.setFormatter(formatter)

logger.addHandler(fileHandler)

app = Flask(__name__)

folder_path = './media/'

class fileInformation:
    def __init__(self, filePath, extractFields):
        self.filePath = filePath
        self.information = extractFields

obj = resumeParser()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def resumedetection():
    if request.method == 'POST':
        f = request.files['filePath']
        f.save(os.path.join(folder_path, f.filename))
        logging.error(f.filename)
        try:
            extractFields = request.form.get('extractFields')
            extractFields = ast.literal_eval(extractFields)
        except (ValueError, SyntaxError) as e:
            extractFields = ast.literal_eval("['name', 'email', 'phone', 'skills']")
        filePath = os.path.join(folder_path, f.filename)
        result = main(filePath)
        if str(result).lower() == "true":
            file = fileInformation(filePath, extractFields)
            dict = obj.extract_data_from_file(file)
            if os.path.exists(filePath):
                os.remove(filePath)
            return render_template('result.html', fileName=f.filename, dict=dict)
            # return dict
        elif str(result).lower() == "false":
            if os.path.exists(filePath):
                os.remove(filePath)
            return "Given File is not a RESUME"
        else:
            return "Something Went Wrong"

@app.route('/resumeparser', methods=['POST'])
def resumeparser():
    try:
        if request.method == 'POST':
            try:
                extractFields = request.form.get('extractFields')
                extractFields = ast.literal_eval(extractFields)
            except (ValueError, SyntaxError) as e:
                extractFields = ast.literal_eval("['name', 'email', 'phone', 'skills']")
            f = request.files['filePath']
            f.save(os.path.join(folder_path, f.filename))
            logging.error(f.filename)
            filePath = os.path.join(folder_path, f.filename)
            file = fileInformation(filePath, extractFields)
            dict = obj.extract_data_from_file(file)
            if os.path.exists(filePath):
                os.remove(filePath)
            return dict
    except:
        return "Something Went Wrong"

if __name__ == '__main__':
    print("Processing of your PDF file is started...")
    app.run(host="0.0.0.0", debug=True, port=5000)