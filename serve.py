from flask import Flask, jsonify, request
app = Flask(__name__)

from window import Root
root = Root()

@app.route('/flush_visited', methods=['GET'])
def flush_visited():
    root.flush_visited()
    return jsonify({'status':'success'}), 200

@app.route('/update', methods=['PATCH'])
def update():
    body_params = request.get_json()
    windows = body_params['windows']
    active_id = body_params['active_id']
    root.add_or_update_windows(windows=windows)
    root.update_active(id=active_id)
    return jsonify({'status':'success'}), 200

@app.route('/get', methods=['GET'])
def get_window():
    input_chars = request.args['input_chars']
    w = root.get_matching(input_chars)
    if w is None:
        return jsonify({'id': None}), 405
    return jsonify({'id': w.id}), 200


if __name__ == '__main__':
      app.run(port=8888, debug=True)
