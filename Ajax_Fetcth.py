# app.py (Flask)
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.get_json()  # JSONデータを取得
    name = data.get('name')
    email = data.get('email')
    
    # 受け取ったデータを処理
    processed_data = {
        "name": name.upper(),
        "email": email.upper()
    }
    
    # 処理したデータをJSONレスポンスとして返す
    return jsonify(processed_data)

if __name__ == '__main__':
    app.run(debug=True)