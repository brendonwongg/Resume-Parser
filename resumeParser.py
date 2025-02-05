from pdfminer.high_level import extract_text
import docx2txt
import re
import subprocess
import nltk
import numpy
import os

nltk.download('stopwords', quiet = True)
nltk.download('punkt_tab', quiet = True)
nltk.download('punkt', quiet = True)
nltk.download('averaged_perceptron_tagger_eng', quiet = True)
nltk.download('maxent_ne_chunker_tab', quiet = True)
nltk.download('words', quiet = True)

Contact_Exp = re.compile(r'[\+\(]?[0-9 .\-\(\)]{8,}[0-9]')
Email_Exp = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')

# extract texts from pdf
def extractTextPDF (pdf_path):
    return (extract_text(pdf_path))

# extract texts from docx
def extractTextDOCX (docs_path):
    #Extract raw text from docx
    text = docx2txt.process(docs_path)

    #replace tabs with spaces so its easier to read
    if text:
        return text.replace('\t', ' ')
    return None

#extract phone number from the text
def extractContact (resume_text):
    #find all that matches with the contact number expression
    contact = re.findall(Contact_Exp, resume_text)
    
    #remove all dashes and special characters from the first number that matches the expression
    #assuming the first match is the applicants contact number
    if contact:
        number = contact[0]

        #checking if the number is in the text again and the length of the number is not too long below 16 characters
        if resume_text.find(number) >= 0 and len(number) < 16:
            return number
        
    return None

#extracting email
def extractEmail (resume_text):
    email = re.findall(Email_Exp, resume_text)
    return email
    #CHANGED RETURN ALL EMAIL JUST TO BE SAFE AND NOT ASSUME

#extract skills from resume
#define skills desired
SKILLS = ['c++', 'communication', 'experience', 'scrum', 'python', 'microsoft office', 'debug', 'array making stuff']

def extractSkills (resume_text):
    #define stop words, the words we want to filter out
    stopWords = set(nltk.corpus.stopwords.words('english'))

    #Tokenize the text in the resume all to single words
    wordTokens = nltk.tokenize.word_tokenize(resume_text)

    #start filtering out the stopwords
    filtered_tokens = []
    for w in wordTokens:
        if w not in stopWords:
            filtered_tokens.append(w)
    
    #now filter out all the punctuations #CHANGE NEEDED TO STILL INCLUDE THE WORDS WITHOUT PUNCTUATION TO NOT EXCLUDE THE WRONG WORD IF THE WORD WITH PUNCTUATION IS A REQUIRED SKILL
    filtered_punctuations = []
    for p in range(len(filtered_tokens)):
        filtered_tokens[p] = re.sub(r'[^\w\s]', '', filtered_tokens[p])

    #generate bigrams and trigrams
    grams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
    foundSkills = set()

    #Go through and see which one word phrase matches the SKILLS
    for x in filtered_tokens:
        if x.lower() in SKILLS:
            foundSkills.add(x)

    #Go through and see which two word phrase matches the SKILLS
    for gram in grams:
        if gram.lower() in SKILLS:
            foundSkills.add(gram)
    
    string = SKILLS[0].lower()

    return foundSkills


RESERVED = ['school', 'college', 'acedemy', 'faculty', 'institute', 'university', 'harvard', 'computer science']
#extract schools
def extractEducation (resume_text):
    #initialise organisation array
    organization = []

    #get all the organisation names first, to be matches with the list of reserved words
    for sentence in nltk.sent_tokenize(resume_text):
        word_tokens = nltk.word_tokenize(sentence)
        pos_tags = nltk.pos_tag(word_tokens)
        pos_ne_chunked = nltk.ne_chunk(pos_tags)
        for chunk in pos_ne_chunked:
            if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
                to_append = ' '.join(c[0] for c in chunk.leaves())
                organization.append(to_append)

    #print("All organization: ", organization)

    #search organization and see which one matches the reserved words
    education = set()
    for org in organization:
        for words in RESERVED:
            if org.lower().find(words) >= 0:
                education.add(org)

    return organization


if __name__ == "__main__":
    #loop through each of the files
    directory = 'resumes'
    for file in os.scandir(directory):
        if file.is_file():

            #extract the text of the file
            #check if its pdf or docx
            if os.path.splitext(file)[1] == '.pdf':
                #extract pdf text
                resume_text = extractTextPDF (file.path)
                #print(resume_text)
            elif os.path.splitext(file)[1] == '.docx':
                resume_text = extractTextDOCX (file.path)
                #print(resume_text)
            else:
                print ("Make sure your resume is either in the format of: PDF and Docx\n")
                continue

            #extract phone number
            phoneNumber = extractContact (resume_text)

            #extract email address
            emailAddress = extractEmail (resume_text)

            #extract skills
            skills = extractSkills (resume_text)

            #extract education
            education = extractEducation (resume_text)

            #print each of them out with their filename
            print(os.path.basename(file), '\n')
            print("Phone Number: ", phoneNumber, "\n")
            print("Email Address: ", emailAddress, "\n")
            print("Matched skills: ", skills, "\n")
            print("Education: ", education, "\n")