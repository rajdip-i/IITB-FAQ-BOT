from flask import Flask, render_template, request, jsonify
from backend import response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form['msg']
    result = response(message)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
