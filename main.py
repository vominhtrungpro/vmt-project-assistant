from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask API!"

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'name': 'Azure',
        'message': 'Hello from Azure!'
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)