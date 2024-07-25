from flask import Flask, jsonify, Response, request
from openai import OpenAI
import os
from flask_cors import CORS
import requests
import json

api_url = 'https://vmt-api-practice.azurewebsites.net/api/Character'

key = os.environ.get('openai_key')

client = OpenAI(api_key=key)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Welcome to the Assistant OpenAI powered by vominhtrungpro@gmail.com!"

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'name': 'Azure',
        'message': 'Hello from Azure!'
    }
    return jsonify(data)

def assistant_response(assistant):
    return {
        'id': assistant.id,
        'created_at': assistant.created_at,
        'description': assistant.description,
        'instructions': assistant.instructions,
        'metadata': assistant.metadata,
        'model': assistant.model,
        'name': assistant.name,
        'object': assistant.object,
        'tools': [tool.type for tool in assistant.tools],
        'response_format': assistant.response_format,
        'temperature': assistant.temperature,
        'tool_resources': {
            'code_interpreter': assistant.tool_resources.code_interpreter,
            'file_search': {
                'vector_store_ids': assistant.tool_resources.file_search.vector_store_ids
            }
        },
        'top_p': assistant.top_p,
    }


@app.route('/api/assistants', methods=['GET'])
def get_assistants():
    assistants = client.beta.assistants.list(
        order="desc",
        limit="20",
    )

    response = [assistant_response(assistant) for assistant in assistants.data]

    return jsonify(response)

def thread_response(thread):
    return {
        'id': thread.id,
        'object': thread.object,
        'created_at': thread.created_at,
        'metadata': {},
        'tool_resources': {},
    }

@app.route('/api/threads',methods=['POST'])
def create_thread():
    thread = client.beta.threads.create()
    return jsonify(thread_response(thread))


@app.route('/api/run',methods=['POST'])
def create_run():    
    if not os.environ.get('is_assistant_enable') == 'True':
        return Response("Currently offline!", mimetype='text/plain')
    
    data = request.get_json()  
    thread_id = data.get('thread_id')
    message = data.get('message')

    thread_message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=message,
    )

    def generate():
        stream = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id="asst_f8T3OBfPEHGrT0viJYGg4Lvg",
            stream=True
        )

        for event in stream:
            if event.event == "thread.message.delta":
                yield f"data: {event.data.delta.content[0].text.value}\n\n"
            
    return Response(generate(), mimetype='text/event-stream')
    


def get_character_names():
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Kiểm tra nếu có lỗi xảy ra
        data = response.json()  # Giả sử API trả về JSON
        
        if data["isSuccess"]:
            names = [character["name"] for character in data["data"]]
            return json.dumps({"isSuccess": True, "name": names})
        else:
            return json.dumps({"isSuccess": False})
    except requests.exceptions.HTTPError as err:
        return json.dumps({"isSuccess": False})
    except Exception as err:
        return json.dumps({"isSuccess": False})

def create_character(name):
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {'name': name}
    
        # Make the POST request
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    
        # Check if the request was successful
        if response.status_code == 200:
            # Return the JSON response
            return json.dumps({"isSuccess": True})
        else:
            return json.dumps({"isSuccess": False})
        
    except requests.exceptions.HTTPError as err:
        return json.dumps({"isSuccess": False})
    except Exception as err:
        return json.dumps({"isSuccess": False})
    
    



def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user", "content": "Create a character name Stelle?"}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_character_names",
                "description": "Get all character names",
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_character",
                "description": "Create a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of character",
                        },
                    },
                    "required": ["name"],
                },
            },
        },
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
            "get_character_names": get_character_names,
            "create_character" : create_character
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            if function_name == "get_character_names":
                function_response = function_to_call(api_url)
            if function_name == "get_current_weather":
                function_response = function_to_call(
                    location=function_args.get("location"),
                    unit=function_args.get("unit"),
                )
            if function_name == "create_character":
                function_response = function_to_call(
                    name=function_args.get("name")
                )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response
    
print(run_conversation())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)