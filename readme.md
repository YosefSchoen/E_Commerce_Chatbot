
# This is my solution for the Conversational Agent.
## Here are the following instructions to set up and run the agent


### Setting up the environment and dependencies
1) Run **pip install -r requirements.txt** to install the necessary packages
2) Before the first run, you need to set up the database by running **setup_db.py**
3) In the **config.json** file, you need to input your openai api in the where it says **OPENAI_API_KEY**



### Running the Agent
1. To run the chatbot, run **app.py** and open your browser to http://127.0.0.1:5000
2. Input a prompt into the text box on the bottom and click send
3. Wait for the chatbot to respond it may take several seconds and repeat
4. You will see the entire running conversation in box on top
5. Enjoy :)

## Testing the Agent
### There are two ways to test the agent 
1) Run the pre-defined tests on the **chatbot_test.py** file.
These tests are designed to test the chatbots use of the tools it has
2) You can interact with the chatbot yourself in the browser 
If you do choose to interact with the chatbot on the browser,
make sure you have a **customer_id** and its corresponding **order_id** from the clean **orders.csv**.



## Understanding the code Structure
### Front End
1) The **templates** folder contains the **index.html** file for the browser
2) The **static** folder contains the **css** and **js** folders 
which contain the files **styles.css** to style,
and **script.js** run the front end

### Back End
1) The file **app.py** is the flask backend of the app 
2) It creates a chatbot and sends messages to it and receives the response

### The Chatbot
1) The main section is the **Chatbot** object in the file **chatbot.py**.
It runs the openai api calls, handles tools, and holds all the messages in the conversation.
### ChatBot Functions and Chatbot Tools
1) The file **chatbot_functions** contains all the functions the chatbot can call in a class called **ChatBotFunctions**
2) The file **chatbot_tools** contains a function used to build a tool for the tool_calls

### The Dummy Data
1) **setup_db.py** contains a program to set up the database using the raw csv files
2) The **dummy_data** folder contains two subfolders
   1) **raw_data** contains the csv files for e-commerce store from a dataset on kaggle
   2) **clean_data** contains the clean simplified data that is used to build the database
3) **dummy_database.db** is a sqlite database that stores the data for the chatbot to use
4) **contact_info.csv** contains the users data for a human representative to use requested in the assignment

### Configurations
1) **config.json** contains all the programs variables such as openai key, model and tool_call data
2) **requirements.txt** contains all the python dependencies to be installed



