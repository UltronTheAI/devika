from flask import Flask, request, jsonify
import subprocess
import time
import threading

app = Flask(__name__)

# Global variable to store the terminal process
terminal = None
output = ""
output_lock = threading.Lock()

def read_output(process):
    global output
    while True:
        line = process.stdout.readline().decode()
        if line == '':
            break
        with output_lock:
            output += line

@app.route('/runCommand', methods=['POST'])
def run_command():
    global terminal, output
    command = request.json['command'].encode('utf-8')
    if terminal is None:
        terminal = subprocess.Popen('cmd', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        threading.Thread(target=read_output, args=(terminal,)).start()
    terminal.stdin.write(command)
    terminal.stdin.write(b'\n')
    terminal.stdin.flush()
    return jsonify({'status': 'Command executed'}), 200

@app.route('/getOutput', methods=['GET'])
def get_output():
    global terminal, output
    if terminal is not None:
        # output = terminal.stdout.readline().decode()
        threading.Thread(target=read_output, args=(terminal,)).start()
        if output == '':
            return jsonify({'error': 'All lines have been read'}), 400
        else:
            return jsonify({'output': output}), 200
    else:
        return jsonify({'error': 'No command has been executed yet'}), 400

@app.route('/new', methods=['GET'])
def new_terminal():
    global terminal
    terminal = subprocess.Popen('cmd', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return jsonify({'status': 'New terminal created'}), 200

@app.route('/reset', methods=['GET'])
def reset_terminal():
    global terminal
    if terminal is not None:
        terminal.kill()
        terminal = None
    return jsonify({'status': 'Terminal reset'}), 200

@app.route('/userinput', methods=['POST'])
def user_input():
    global terminal
    user_input = request.json['input'].encode('utf-8')
    if terminal is not None:
        terminal.stdin.write(user_input)
        terminal.stdin.write(b'\n')
        terminal.stdin.flush()
        return jsonify({'status': 'User input sent'}), 200
    else:
        return jsonify({'error': 'No command has been executed yet'}), 400

@app.route('/changedir', methods=['POST'])
def change_dir():
    global terminal
    directory = request.json['directory']
    if terminal is not None:
        terminal.stdin.write(f'cd {directory}'.encode())
        terminal.stdin.write(b'\n')
        terminal.stdin.flush()
        return jsonify({'status': 'Directory changed'}), 200
    else:
        return jsonify({'error': 'No command has been executed yet'}), 400

@app.route('/runApp', methods=['POST'])
def run_app():
    global terminal, output
    app_name = request.json['app_name']
    if terminal is None:
        terminal = subprocess.Popen(app_name, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        threading.Thread(target=read_output, args=(terminal,)).start()
    return jsonify({'status': 'App started'}), 200

@app.route('/postInputToApp', methods=['POST'])
def post_input_to_app():
    global terminal
    user_input = request.json['input'].encode('utf-8')
    if terminal is not None:
        terminal.stdin.write(user_input)
        terminal.stdin.write(b'\n')
        terminal.stdin.flush()
        terminal.stdin.close()
        time.sleep(1)
        # terminal.communicate(input=user_input)
        return jsonify({'status': 'User input sent to app'}), 200
    else:
        return jsonify({'error': 'No app has been started yet'}), 400

@app.route('/closeApp', methods=['GET'])
def close_app():
    global terminal
    if terminal is not None:
        terminal.kill()
        terminal = None
        return jsonify({'status': 'App closed'}), 200
    else:
        return jsonify({'error': 'No app has been started yet'}), 400

@app.route('/outputofapp', methods=['GET'])
def output_of_app():
    global terminal, output
    if terminal is not None:
        with output_lock:
            if output == '':
                return jsonify({'error': 'All lines have been read'}), 400
            else:
                result = output
                output = ""
                return jsonify({'output': result}), 200
    else:
        return jsonify({'error': 'No app has been started yet'}), 400

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
