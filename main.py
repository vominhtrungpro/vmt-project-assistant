from flask import Flask, jsonify, Response, request
from openai import OpenAI
import os
from flask_cors import CORS

key = os.environ.get('openai_key')

client = OpenAI(api_key=key)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Welcome to the Assistant OpenAI powered by Trung Vo!"

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
            if event.event == "thread.message.completed":
                yield f"data: {event.data.content[0].text.value}\n\n"
            
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)