import pdfplumber
from re import sub #To clean text using 
from re import escape
from pickle import load #To load the trained model and the vectorizer
from os.path import isfile #To check validity of a path
from os import getcwd as cd #To get current working directory
from os.path import abspath #To get absolute path
from docx2txt import process #To process docx files

#Dictionary containing keywords for file types (makes writing functions easier)
file_format_table = {
    'doc' : "Document",
    'docx' : "Document",
    'pdf' : "Book",
    'txt' : "ASCII"
}

#Gets path to current directory (containing this code file) and replaces backslashes with forward slashes (hence usable on all OSs)
curr_dir_path = abspath(cd()).replace("\\", "/")

#Use absolute path to find the trained model (CV Classifier) and the text vectorizer (CV Vectorizer) to load them
model_path = f"{curr_dir_path}/resources/CVClassifier.sav"
vectorizer_path = f"{curr_dir_path}/resources/CVVectorizer.sav"
model = load(open(model_path, "rb"))
vector = load(open(vectorizer_path, "rb"))

#Checks file extension, extracts data based on the extension and returns cleaned data by way of the clean_text function
def extract_data(file_path):
    file_format = check_format(file_path)
    with open(file_path, "r") as f:
        if file_format == "ASCII": #txt file, read using inbuilt methods
            file_text = f.read()
        elif file_format == "Document": #Word file, read using docx2txt module
            file_text = process(file_path)
        elif file_format == "Book": #PDF file, read using PyMuPDF (fitz)
            pdf = pdfplumber.open(file_path)
            file_text= ""
            for page in pdf.pages:
              file_text += page.extract_text() + "\n"
            pdf.close()
    return clean_text(file_text)

#Returns input file format by finding the last '.' as a basis, and then checking the keyword in the file_format_table
def check_format(file_path):
    file_format = file_path[file_path.rfind(".") + 1:]
    return file_format_table[file_format]

#Uses regex to clean the text, then returns it by splitting it into tokens (words)
def clean_text(file_text):
    file_text = sub('httpS+s*', ' ', file_text) #Remove links
    file_text = sub('RT|cc', ' ', file_text) #Remove RT (retweet) and cc tags
    file_text = sub('#S+', '', file_text) #Remove hashtags
    file_text = sub('@S+', '  ', file_text) #Remove @mentions
    file_text = sub('[%s]' % escape("""!"#$%&'()*+,-./:;<=>?@[]^_`{|}~"""), ' ', file_text) #Remove special characters
    file_text = sub(r'[^x00-x7f]',r' ', file_text)  #Remove non ASCII characters
    file_text = sub('\s+', ' ', file_text) #Remove extra whitespaces
    return file_text

# file_path = str(input("Please enter the path to the file: "))

def main(file_path):
    # Check to see if the path leads to a file and if it exists
    if isfile(file_path):
        text = extract_data(file_path)
        text = vector.transform([text]) #Vectorize text into a format recognizable by the model
        result = bool(model.predict(text)) #THe model returns a 1 (CV) or 0 (Not CV) value, make it Boolean for ease of understanding
        return result
    else:
        return "Something Went Wrong with file"

# Sample file for testing
# P:\Internship Work\Tenup Software Services LLP\CV Detector\Test Files\Backend-Developer-Resume.pdf