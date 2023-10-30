from flask import Flask, render_template, request, jsonify


from flask import Flask, render_template, request, jsonify

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer,ChatterBotCorpusTrainer

import spacy
from spacy.cli.download import download
import pandas as pd
nlp = spacy.load('en_core_web_sm')

# -*- coding: utf-8 -*-
import chatterbot.corpus
from chatterbot import comparisons
from chatterbot import response_selection
from chatterbot import ChatBot
from chatterbot.comparisons import LevenshteinDistance
from chatterbot.response_selection import get_first_response
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer

global last_reply

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/home")
def home():
    return render_template('chat.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/share", methods=["GET", "POST"])
def share_on_whatsapp():
    global last_reply
    # Message to be shared
    message = last_reply
    
    # WhatsApp URL with pre-defined message
    whatsapp_url = f"https://api.whatsapp.com/send?text={message}"
    
    return render_template('share.html', whatsapp_url=whatsapp_url)

@app.route('/generate_file')
def generate_file():
    global last_reply
    file_content = last_reply
    file_content = file_content.replace("*", " ")
    file_content = file_content.replace("_", " ")
    file_content = file_content.replace("%0a", "\n")
    return file_content

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    return get_Chat_response(input)

def get_Chat_response(text):
    global last_reply
    #nlp = spacy.load("en_core_web_sm")
    # Create a new chat bot named Charlie
    chatbot = ChatBot('Charlie')

    trainer = ListTrainer(chatbot)

    threshold=0
    #question = "fish"
    #question = "what does Conversational AI refer to?"

    response = get_answer(covid_faq_chatbot, text, threshold)
    #trainer = ChatterBotCorpusTrainer(chatbot)
    
    #trainer.train('C:\\Users\\sanje\\OneDrive\\Documents\\GIT\\GCPLP_practice_module\\GCPLP_practice_module\\chatbot\\covid.yml')
    
    """
    # Load data from CSV
    df = pd.read_csv('testforkb.csv')

    # Convert the DataFrame to a list of dictionaries
    custom_data = df.to_dict(orient='records')

    trainer = ListTrainer(chatbot)

    # Train the chatbot using the custom data
    trainer.train(custom_data)
    
    response = str(chatbot.get_response(text))
    print (response)
    """
    last_reply = response
    last_reply = last_reply.replace("<b>", "*")
    last_reply = last_reply.replace("</b>", "*")
    last_reply = last_reply.replace("<u>", "_")
    last_reply = last_reply.replace("</u>", "_") 
    last_reply = last_reply.replace("<br>", "%0a")
    multi_cal= 'hi'
    return response

def faq_chatbot_initialize(chatbot_name, threshold=0.9, excel_path= 'C:\\Users\\sanje\\data\\testforkb.xlsx', worksheet_name='Recipe'):
    covid_faq_chatbot = ChatBot(
        chatbot_name,
        logic_adapters=[
            {
                "import_path": "chatterbot.logic.BestMatch",
                "statement_comparison_function": LevenshteinDistance,
                "response_selection_method": get_first_response,
                "maximum_similarity_threshold": threshold
            }
        ],
        preprocessors=[
            'chatterbot.preprocessors.clean_whitespace'
        ],
        read_only=True,
    )
    trainer = ListTrainer(covid_faq_chatbot)
    #trainer.train("chatterbot.corpus.english")
    # read questions and answers
    data = pd.read_excel(excel_path, sheet_name=worksheet_name, engine='openpyxl')
    question = data.get('Ingredients')
    answer = data.get('Recipe')

    #for i in range(0, 3):
    #    print('[Q]', question[i], '\n[A]', answer[i], '\n\n')

    # Iteratively adding the question and answer
    train_list = []
    for i in range(len(question)):
        train_list.append(question[i])
        train_list.append(answer[i])
    # train the faq
    trainer.train(train_list)
    #trainer.export_for_training('covid.yml')
    print("was here")
    return covid_faq_chatbot

def get_answer(faq_chatbot, question, threshold):  # let's get a response to our input
    # try suggested corpora to find best fit. If first corpus < theshold, try another.
    # avoid random responses confidence 0
    response = faq_chatbot.get_response(question)
    if  response.confidence < threshold:  # not a good answer, look elsewhere
        #response = nlp_chatbot.get_response(question)
        print(response)
        print(response.confidence)
        response = 'We do not have such a combination in our corpus. Remove some ingredients and try again.'
    else:
        print(response)
        print(response.confidence)
        response = response.serialize()['text']
        response = response.replace("splt","<br>")
        print (response)
    return response
#import logginglogging.basicConfig(level=logging.INFO)    # Enable info level logging

    
if __name__ == '__main__':
    data_path = 'data/'
    excel_name =  'C:\\Users\\sanje\\data\\testforkb.xlsx'
    worksheet_name = 'Recipe'

    print ("train")
    covid_faq_chatbot = faq_chatbot_initialize("Recipe Bot", excel_path=excel_name, worksheet_name=worksheet_name)

    app.run()
