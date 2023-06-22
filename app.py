import os
import ast
from resume_detector import main
from resume_parser import resumeParser
from flask import Flask, request, render_template

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
        elif str(result).lower() == "false":
            if os.path.exists(filePath):
                os.remove(filePath)
            return "Given File is not a RESUME"
        else:
            return "Something Went Wrong"

if __name__ == '__main__':
    print("Processing of your PDF file is started...")
    app.run(host="0.0.0.0", debug=True, port=5000)