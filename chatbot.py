import openai
import json
from typing import List, Dict, Callable, Union
from sqlalchemy import create_engine, text
import inspect
from chatbot_functions import ChatBotFunctions
from chatbot_tools import ChatBotTools
from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletion, ChatCompletionMessage


with open('config.json') as f:
    config = json.loads(f.read())


class Chatbot:
    def __init__(self) -> None:
        """
        the constructor will make the following members of the class
        tools: a list of tool dictionaries for the openai client
        available functions: a dictionary of all the functions to call with the openai tool calls
            the dictionary will be in the following format key = function name value is function object
        messages: a list of messages in the chat so far
        client: the openai client to talk with
        """

        with open('tools.json') as f:
            tools_dict = json.loads(f.read())
        self.tools = list(map(lambda tool_name: ChatBotTools.get_tool(tool_name), tools_dict['tools']))
        self.available_functions = self.get_available_functions()
        self.messages = self.get_starting_messages()
        self.client = openai.Client(
            api_key=config['openai']['OPENAI_API_KEY'],
            timeout=config['openai']['timeout'],
            max_retries=config['openai']['max_retries'])

    @staticmethod
    def get_available_functions() -> Dict[str, Callable[[], str]]:
        """
        will create a dictionary of functions available for the tool_calls to use
        :return: the dictionary of functions
        """

        members = inspect.getmembers(ChatBotFunctions, inspect.isfunction)
        available_functions = {name: func for name, func in members}
        return available_functions

    @staticmethod
    def get_table_definitions_prompt() -> str:
        """
        will create a prompt for the chatbot to let it know it has access to the table,
        and it will give the chatbot the table definition
        :return: the prompt
        """

        # getting the prompt about table definitions
        prompt = config['prompts']['table_definitions']

        # will add a table definition for each table
        for name in config['database']['tables_names']:
            engine = create_engine(config['database']['name'])

            # querying the db for the table definition
            with engine.connect() as conn:
                query = f"PRAGMA table_info({name});"
                result = conn.execute(text(query))

            # reformating the output as a string for the prompt
            table_definition = f'{name}(' + '\n\t'.join(
                list(map(
                    lambda column: f'{column[1]}: {column[2]}',
                    result.all()
                ))
            ) + '\n)'

            prompt += table_definition + '\n'

        return prompt

    def get_function_definition_prompt(self) -> str:
        """
        gets the name and args of the functions the chatbot can call
        this is put into the system prompt to reduce function name and arg name hallucinations
        :return: the prompt of function definitions
        """
        prompt = config['prompts']['function_definitions']

        for name, func in self.available_functions.items():
            args = tuple(inspect.getfullargspec(self.available_functions[name]).args)
            prompt += name+str(args)+'\n'

        return prompt+'\n'

    def get_starting_messages(self) -> List[Union[Dict[str, str], ChatCompletionMessage]]:
        """
        This function will create the first prompt for the system role.
        It will tell the AI what it job is as an assistant for an ecommerce store also it knows the return policies
        for the store also it will get the function and table definitions
        :return: a list of messages containing the initial system message
        """

        # this is the systems starting prompt to start a chatbot session
        prompt = config['prompts']['system']

        # will add function definitions and table definitions to the system prompt
        # this helps the system not hallucinate names of tables and functions
        prompt += self.get_function_definition_prompt()
        prompt += self.get_table_definitions_prompt()

        # the chatbot also will get the stores return policies
        for k, v in config['prompts']['return_policy'].items():
            prompt += v

        messages = [{'role': 'system', 'content': prompt}]
        return messages

    def get_response_prompt(self) -> ChatCompletion:
        """
        this is the basic procedure of working with openai chat completions
        get a prompt and ask the client to send a response
        :return: the chatbots response
        """

        # creating the chat completion and receiving the response message
        response = self.client.chat.completions.create(
            model=config['openai']['model'],
            messages=self.messages,
            tools=self.tools,
            tool_choice=config['openai']['tool_choice'],
            temperature=config['openai']['temperature']
        )

        return response

    def handle_tool_call(self, tool_call: ChatCompletionMessageToolCall) -> Dict[str, str]:
        """
        this function will handle any tool call the chatbot decides it needs
        :param tool_call: the tool call to handle
        :return: the final message from the tool call
        """

        # will get the function to call and its arguments then call it
        function_to_call = self.available_functions.get(
            tool_call.function.name,
            ChatBotFunctions.function_not_found
        )

        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(**function_args)

        response = {
            'tool_call_id': tool_call.id,
            'role': "tool",
            'name': tool_call.function.name,
            'content': function_response,
        }

        return response

    def handle_tool_calls(self, tool_calls: List[ChatCompletionMessageToolCall]) -> ChatCompletion:
        """
        this will handle all the tool_calls sequentially and get the chatbots response to them
        :param tool_calls: the list of tools to call
        :return: the response message
        """

        # will handle all chained tool calls sequentially and return the responses to the chatbot
        self.messages += list(map(
            lambda tool_call: self.handle_tool_call(tool_call),
            tool_calls))

        # will get the clients response to the tool calls
        response = self.client.chat.completions.create(
            model=config['openai']['model'],
            messages=self.messages,
            temperature=config['openai']['temperature']
        )
        return response

    def run_chat(self, prompt: str) -> str:
        """
        This is the main function of the chatbot that the flask app will interact with
        it receives a prompt from the user the generates a sequence of tool calls if any,
        and it outputs the response from the chatbot
        :param prompt: the users question
        :return: the chatbots response
        """
        self.messages.append({'role': 'user', 'content': prompt})
        response_message = self.get_response_prompt().choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            self.messages.append(response_message)
            response = self.handle_tool_calls(tool_calls).choices[0].message
            self.messages.append(response)
            return response.content

        self.messages.append(response_message)
        return response_message.content
