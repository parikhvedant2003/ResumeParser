import re
import spacy
import logging
import textract
import docx2txt
import pdfplumber
import pandas as pd
from spacy.matcher import Matcher
from retrain_model import model, vectorizer, positive_cases, negative_cases

nlp = spacy.load('en_core_web_sm')

matcher = Matcher(nlp.vocab)

class informationExtractor:

    def extract_text_from_document(document_filename):
        if document_filename.endswith('docx'):
            try:
                text = docx2txt.process(document_filename)
            except Exception as e:
                logging.error('Error in docx file:: ' + str(e))
                return [], " "
        else: # For doc files
            try:
                text = textract.process(document_filename).decode('utf-8')
                return text
            except KeyError:
                logging.error("Something went wrong")
                return ' '        
        try:
            clean_text = re.sub(r'\n+', '\n', text)
            clean_text = clean_text.replace("\r", "\n")
            clean_text = clean_text.replace("\t", " ")  # Normalize text blob
            resume_lines = clean_text.splitlines()  # Split text blob into individual lines
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if line.strip()]  # Remove empty strings and whitespaces
            return resume_lines, text
        except Exception as e:
            logging.error('Error in extracted text from file:: ' + str(e))
            return [], " "

    # This function is extracting text from PDF file
    def extract_text_from_pdf(pdf_file):
        try:
            pdf = pdfplumber.open(pdf_file)
            raw_text= ""
            for page in pdf.pages:
              raw_text += page.extract_text() + "\n"
            pdf.close()
        except Exception as e:
            logging.error('Error in pdf file:: ' + str(e))
            return [], " "
        try:
            # It will remove all unneccessary spaces from the extracted text of PDF file
            full_string = re.sub(r'\n+', '\n', raw_text)
            full_string = full_string.replace("\r", "\n")
            full_string = full_string.replace("\t", " ")
            full_string = re.sub(r"\uf0b7", " ", full_string)
            full_string = re.sub(r"\(cid:\d{0,2}\)", " ", full_string)
            full_string = re.sub(r'• ', " ", full_string)
            resume_lines = full_string.splitlines(True)
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if line.strip()]
            return resume_lines, raw_text
        except Exception as e:
            logging.error('Error in pdf file words:: ' + str(e))
            return [], " "

    # This function is extracting Mobile Number from extracted text of PDF file
    def extract_mobile_number(extracted_text):
        extracted_text = extracted_text.replace("(", "")
        extracted_text = extracted_text.replace(")", "")
        extracted_text = extracted_text.replace("-", "")
        extracted_text = extracted_text.replace(".", "")
        extracted_text = extracted_text.replace("[", "")
        extracted_text = extracted_text.replace("]", "")
        # To cover all kind of patterns of representing mobile numbers, we have applied the patterns given below
        extracted_numbers = re.findall(re.compile(r'\b\d{10}\b'), extracted_text[::-1])
        extracted_numbers.extend(re.findall(re.compile(r'\d{10}\b'), extracted_text))
        extracted_numbers.extend(re.findall(re.compile(r'\b\d{11}\b'), extracted_text))
        extracted_numbers.extend(re.findall(re.compile(r'\b\d{5}[\s.,-]\d{5}\b'), extracted_text[::-1]))
        extracted_numbers.extend(re.findall(re.compile(r'\b\d{6}[\s.,-]\d{4}\b'), extracted_text[::-1]))
        extracted_numbers.extend(re.findall(re.compile(r'\b\d{4}[\s.,-]\d{6}\b'), extracted_text[::-1]))
        extracted_numbers.extend(re.findall(re.compile(r'\b\d{4}[\s.,-]\d{3}[\s.,-]\d{3}\b'), extracted_text[::-1]))
        extracted_numbers.extend(re.findall(re.compile(r'\b\d{3}[\s.,-]\d{4}[\s.,-]\d{3}\b'), extracted_text[::-1]))
        extracted_numbers.extend(re.findall(re.compile(r'\b\d{4}[\s.,-]\d{4}[\s.,-]\d{2}\b'), extracted_text[::-1]))
        extracted_numbers.extend(re.findall(re.compile(r'\b\d{4}[\s.,-]\d{2}[\s.,-]\d{4}\b'), extracted_text[::-1]))
        extracted_numbers.extend(re.findall(re.compile(r'\b\d{2}[\s.,-]\d{4}[\s.,-]\d{4}\b'), extracted_text[::-1]))

        mobile_numbers = []
        if extracted_numbers:
            for number in extracted_numbers:
                number = list(number)
                while(1):
                    if "." in number:
                        number.remove(".")
                    elif "-" in number:
                        number.remove("-")
                    elif " " in number:
                        number.remove(" ")
                    else:
                        break
                number = ''.join(number)
                if number in extracted_text:
                    mobile_numbers.append(number)
                else:
                    mobile_numbers.append(number[::-1])
            mobile_numbers = list(set(mobile_numbers))
            return str(mobile_numbers[0])
        logging.error('Error in detection of Mobile Number')
        return None

    # This function is extracting Email ID from extracted text of PDF file
    def extract_email(extracted_text):
        try:
            email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", extracted_text)
            if email:
                try:
                    return str(email[0].split()[0].strip(';'))
                except IndexError:
                    logging.error('Error in indexing of detected email addresses')
                    return None
            else :
                return None
        except:
            return None

    # This function is extracting Candidate Name from extracted text of PDF file
    def extract_name(extracted_text, wholeText):
        if wholeText == "":
            return None
        if extracted_text == "":
            extracted_text = wholeText
        extracted_text = extracted_text.replace(".", " ")
        extracted_text = extracted_text.lower()
        nlp_text = nlp(extracted_text)
        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
        matcher.add('NAME', [pattern])
        matches = matcher(nlp_text)
        candidate_name = ""
        for match_id, start, end in matches:
            span = nlp_text[start:end]
            candidate_name = str(span.text)
            if candidate_name != "" and candidate_name.isalpha() and ((model.predict(vectorizer.transform([candidate_name])) == 1) and not (candidate_name in negative_cases)):
                return candidate_name.upper()
        possible_names = []
        words = list(extracted_text.split(' '))
        for word in words:
            if word.isalpha() and (len(word) > 1):
                candidate_name = str(word).lower()
                if ((model.predict(vectorizer.transform([candidate_name])) == 1) and not (candidate_name in negative_cases)) or ((model.predict(vectorizer.transform([candidate_name])) == 0) and (candidate_name in positive_cases)):
                    possible_names.append(candidate_name)
        possible_names = list(set(possible_names))
        candidate_names = []
        if len(possible_names) == 0:
            logging.error('Can\'t detect of Candidate Name from the contact-info segment')
            name = informationExtractor.extract_name(wholeText, "")
            if name:
                return name            
        if len(possible_names) == 1:
            return possible_names[0].upper()
        # To cover the Names like "Jignesh R. Prajapati"
        middlenames = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        for i in possible_names:
            for j in possible_names:
                if ((i + " " + j) in extracted_text) and not ((i + " " + j) in negative_cases):
                    candidate_names.append((i + " " + j).upper())
                if ((j + " " + i) in extracted_text) and not ((j + " " + i) in negative_cases):
                    candidate_names.append((j + " " + i).upper())
                for middlename in middlenames:
                    if (((i + " " +  middlename + " " + j) in extracted_text) or ((i + " " +  middlename + "  " + j) in extracted_text)) and not (((i + " " +  middlename + " " + j) in negative_cases) or ((i + " " +  middlename + "  " + j) in negative_cases)):
                        candidate_names.append((i + " " +  middlename + " " + j).upper())
        candidate_names = list(set(candidate_names))
        if len(candidate_names) == 0:
            indices = [extracted_text.find(name) for name in possible_names]
            min_index = min(indices)
            for name in possible_names:
                if extracted_text.find(name) == min_index:
                    return name.upper()
        elif len(candidate_names) != 1:
            indices = [extracted_text.find(i.lower()) for i in candidate_names]
            min_index = min(indices)
            for name in candidate_names:
                if extracted_text.find(name.lower()) == min_index:
                    return name.upper()
        else:
            return candidate_names[0].upper()
        return None

    # This function is extracting skills from extracted text of PDF file
    def extract_skills(extracted_text):
        # skills.txt is used to extract skills from PDF file and extracts only those skills which are already present in txt file
        skills_data = pd.read_csv("./resources/skills.txt", header=None, names=['Data'])
        skills_data = skills_data.set_index('Data').T
        nlp_text = nlp(extracted_text)
        tokens = [token.text.lower() for token in nlp_text if not token.is_stop]
        skills = list(skills_data.columns.values)
        for skill in skills:
            skill = skill.lower()
        skillset = []
        for token in tokens:
            if token in skills:
                skillset.append(token)
        for skill in skills:
            if skill in tokens:
                skillset.append(skill)
        joined = []
        for index in range(len(tokens) - 1):
            if tokens[index].isalnum():
                joined.append(" ".join([tokens[index], tokens[index + 1]]).lower())
        for skill in joined:
            if skill in skills:
                skillset.append(skill)
        for skill in skills:
            if skill in joined:
                skillset.append(skill)
        if skillset:
            return [skill.upper() for skill in set([skill.lower() for skill in skillset])]
        else:
            return None