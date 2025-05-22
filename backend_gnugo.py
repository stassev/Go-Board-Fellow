#Copyright (C) Svetlin Tassev

# This file is part of Go Board Fellow

# Go Board Fellow is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later version

# Go Board Fellow is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details

# You should have received a copy of the GNU General Public License along 
# with Go Board Fellow. If not, see <https://www.gnu.org/licenses/>.

from flask import Flask, request, jsonify
import subprocess
import tempfile

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    return response

@app.route('/next-move', methods=['POST'])
def next_move():
    sgf = request.json['sgf']
    color = request.json.get('color', 'black').lower()
    gtp_color = 'b' if color.startswith('b') else 'w'
    strength = request.json.get('strength', 5)  # Default to 5
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.sgf') as f:
        f.write(sgf.encode())
        f.flush()
        # Run gnugo with strength setting
        proc = subprocess.Popen(
            ['gnugo', '--mode', 'gtp', '--infile', f.name, '--level', str(strength)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        proc.stdin.write(f'genmove {gtp_color}\n')
        proc.stdin.flush()
        output = proc.stdout.readline()
        proc.terminate()
    return jsonify({'move': output.strip()})

if __name__ == '__main__':
    app.run(port=5000)
