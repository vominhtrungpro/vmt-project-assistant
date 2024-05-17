from flask import Flask, jsonify
from openai import OpenAI
import json


key = 'sk-proj-P4D1YHceWNYKCpnohX2jT3BlbkFJzRrP66MSh5f2m8H1nT0a'

client = OpenAI(api_key=key)

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Assistant OpenAI!"

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

    assistants_list = [assistant_response(assistant) for assistant in assistants.data]

    return jsonify(assistants_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)