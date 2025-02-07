import json
from datetime import datetime
import requests
from utils.tavily import tavily_search

def get_current_time():
    """Get the current time for a given location"""
    return json.dumps({"current_time": datetime.now().strftime("%I:%M %p") })

def perform_calculation(operation, numbers):
    """Perform a mathematical calculation on a list of numbers"""
    print(f"perform_calculation called with operation: {operation}, numbers: {numbers}")
    if operation == "add":
        result = sum(numbers)
    elif operation == "subtract":
        result = numbers[0] - sum(numbers[1:])
    elif operation == "multiply":
        result = 1
        for num in numbers:
            result *= num
        print(f"Result:{result}")
    elif operation == "divide":
        result = numbers[0]
        for num in numbers[1:]:
            result /= num
    else:
        raise ValueError("Invalid operation")
    return json.dumps({"operation": operation, "numbers": numbers, "result": result})

def get_weather(location):
    """
    Gets the current weather for the given location.

    Parameters:
    location (str): The name of the location to get the weather for.
    api_key (str): Your API key for the weather service.

    Returns:
    dict: Weather data for the location or an error message.
    """
    base_url = "http://api.openweathermap.org/data/3.0/weather"
    api_key = ""
    params = {
        'q': location,
        'appid': api_key,
        'units': 'metric'  # or 'imperial' for Fahrenheit
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Location not found or API request failed'}
def get_tools():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current time in a given location"
            }
        },
        {
            "type": "function",
            "function": {
                "name": "perform_calculation",
                "description": "Perform a mathematical calculation on a list of numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "The operation to perform: add, subtract, multiply, divide",
                            "enum": ["add", "subtract", "multiply", "divide"]
                        },
                        "numbers": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "The list of numbers to perform the operation on",
                        },
                    },
                    "required": ["operation", "numbers"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search realtime information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"],
                }
            }
        }
    ]
    return tools

def handle_tool_call(tool_call):
    function_response = None
    if tool_call.function.name == "get_current_time":
        function_args = json.loads(tool_call.function.arguments)
        function_response = get_current_time()
    if tool_call.function.name == "perform_calculation":
        function_args = json.loads(tool_call.function.arguments)
        function_response = perform_calculation(
            operation=function_args.get("operation"), 
            numbers=function_args.get("numbers")
        )
    if tool_call.function.name == "search":
        function_args = json.loads(tool_call.function.arguments)
        res = tavily_search(
            query=function_args.get("query")
        )
        if res is not None:
            function_response = json.dumps(res)
    if function_response is not None:
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_call.function.name,
            "content": function_response,
        }
    return None