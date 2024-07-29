import json
from typing import List, Dict


with open('config.json') as f:
    config = json.loads(f.read())

with open('tools.json') as f:
    tools = json.loads(f.read())

class ChatBotTools:
    @staticmethod
    def get_properties(args: List[List[str]]) -> Dict[str, Dict[str, str]]:
        """
        this function build the properties section of the tool
        :param args: the arguments of the function openai will call
        :return: returns the args in the correct format for the openai api for tool_calls
        """
        properties = {}
        for arg in args:
            arg_name, arg_type, arg_description = arg
            properties[arg_name] = {
                'type': arg_type,
                'description': arg_description
            }
        return properties

    @staticmethod
    def get_tool(tool_name: str) -> Dict:
        """
        this function will get the name, description args, and required args of a tool from the tools in the config file
        and will build the tool dictionary according to the openai specs
        :param tool_name: the name of the tool to build
        :return: the tool as a dictionary in the correct format for openai
        """
        tool_confing = tools['tools'][tool_name]
        name = tool_confing['name']
        description = tool_confing['description']
        args = tool_confing['args']
        required_args = tool_confing['required_args']

        tool = {
            'type': 'function',
            'function': {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": ChatBotTools.get_properties(args),
                    "required": required_args
                }
            }
        }

        return tool
