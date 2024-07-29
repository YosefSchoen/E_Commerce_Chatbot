# app.py
from flask import Flask, request, jsonify, render_template
from chatbot import Chatbot

app = Flask(__name__)
bot = Chatbot()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """
    will get the users prompt send it to the chatbot and send the response to the browser
    :return: the chatbots response
    """
    user_input = request.json.get('message')
    response = bot.run_chat(user_input)
    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True)
