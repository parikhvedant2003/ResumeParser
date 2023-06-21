import logging
from resume_segmentation import segmentation
from information_extractor import informationExtractor

class resumeParser():
    # This is the main file from where execution is starting
    def extract_data_from_file(self, file):
        if file.filePath.endswith('doc'):
            try:
                # extract_text_from_pdf returns the extracted text from the PDF file
                resume_lines, raw_text = informationExtractor.extract_text_from_document(file.filePath)
                if (not resume_lines) and (raw_text == ''):
                    logging.error('No resume data can be fetch from doc file')
                    logging.error('File should not contain information in images')
            except:
                logging.error('No resume data can be fetch from file')
                return None
        elif file.filePath.endswith('docx'):
            try:
                # extract_text_from_pdf returns the extracted text from the PDF file
                resume_lines, raw_text = informationExtractor.extract_text_from_document(file.filePath)
                if (not resume_lines) and (raw_text == ''):
                    logging.error('No resume data can be fetch docx from file')
                    logging.error('File should not contain information in images')
            except:
                logging.error('No resume data can be fetch from file')
                return None
        elif file.filePath.endswith('pdf'):
            try:
                # extract_text_from_pdf returns the extracted text from the PDF file
                resume_lines, raw_text = informationExtractor.extract_text_from_pdf(file.filePath)
                if (not resume_lines) and (raw_text == ''):
                    logging.error('No resume data can be fetch from PDF file')
                    logging.error('PDF file should not contain information in images')
            except:
                logging.error('No resume data can be fetch from PDF file')
                return None
        elif file.filePath.endswith('txt'):
            with open(file, 'r', encoding='latin') as f:
                resume_lines = f.readlines()
        else:
            resume_lines = None

        # here infromation_to_find is having values of the attributes whose values we want to extract from PDF file
        information_to_find = file.information
        # response is having the values of the attributes whose values we want to extract from PDF file
        response = {}
        # resume_segments are having values from different segments of PDF file
        resume_segments = segmentation.segment(resume_lines)

        extracted_text = " ".join(resume_lines)

        if "email" in information_to_find:
            email = informationExtractor.extract_email(extracted_text)
            response['email'] = email
        if "name" in information_to_find:
            try: 
                name = informationExtractor.extract_name(" ".join(resume_segments['contact_info']).replace(email[0], ""), extracted_text.replace(email[0], ""))
                response['name'] = name
            except:
                name = informationExtractor.extract_name(" ".join(resume_segments['contact_info']), extracted_text)
                response['name'] = name
        if "phone" in information_to_find:
            try:
                phone = informationExtractor.extract_mobile_number(extracted_text)
                response['phone'] = phone
            except:
                logging.error('Error while matching pattern to identify Mobile Number')
                phone = None
                response['phone'] = phone
        if "skills" in information_to_find:
            try:
                skills = informationExtractor.extract_skills(extracted_text)
                response['skills'] = skills
            except:
                logging.error('Error while extracting skills from PDF file')
                skills = None
                response['skills'] = skills
        return response