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
from sgfmill import sgf, boards
import re

def is_gtp_move(s):
    # Matches one or two letters (skipping 'I'), followed by one or two digits
    # For standard Go, column is A-H,J-T (skips I), row is 1-19
    return re.fullmatch(r'[A-HJ-T][A-HJ-T]?\d{1,2}', s) is not None
app = Flask(__name__)

# Set this to False to disable printing KataGo input/output
DEBUG = True

def coord_to_gtp(row, col):
    # row and col are 0-based, top-left is (0,0)
    # GTP columns: A=0, B=1, ..., H=7, J=8 (skips I), ..., T=18
    # GTP rows: 1=bottom, 19=top (if (0,0) is top-left, need to invert row)
    # So: GTP column is col, GTP row is 19 - row
    gtp_col = chr(ord('A') + col + (1 if col >= 8 else 0))  # Skip 'I'
    gtp_row = row+1
    return f"{gtp_col}{gtp_row}"

def print_if_debug(msg, source="stdout"):
    if DEBUG:
        print(f"[KataGo {source}] {msg}", end='')

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    return response

@app.route('/next-move', methods=['POST'])
def next_move():
    sgf_data = request.json['sgf']
    color = request.json.get('color', 'black').lower()
    gtp_color = 'b' if color.startswith('b') else 'w'
    strength = int(request.json.get('strength', 10))
    visits = 40 * strength  # Adjust as needed

    try:
        sgf_game = sgf.Sgf_game.from_string(sgf_data)
    except Exception as e:
        return jsonify({'error': f'Failed to parse SGF: {str(e)}'}), 400

    board_size = sgf_game.get_size()
    if board_size not in (9, 13, 19):
        return jsonify({'error': f'Unsupported board size: {board_size}'}), 400

    root = sgf_game.get_root()
    moves = []
    
    # Add setup stones (AB and AW)
    if root.has_property('AB'):
        for stone in root.get('AB'):
            moves.append(('b', stone))
    if root.has_property('AW'):
        for stone in root.get('AW'):
            moves.append(('w', stone))
    
    # Add mainline moves (B and W)
    node = root
    while node:
        if node.has_property('B'):
            moves.append(('b', node.get('B')))
        elif node.has_property('W'):
            moves.append(('w', node.get('W')))
        node = node.next()
    
    katago_cmd = [
        'katago', 'gtp',
        '-model', './kata1-stongest.bin.gz',
        '-config', './katago.cfg'
    ]

    proc = subprocess.Popen(
        katago_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # List all GTP commands we will send
        gtp_commands = []
        gtp_commands.append(f'boardsize {board_size}\n')
        gtp_commands.append('clear_board\n')
        #gtp_commands.append(f'kata-set-param maxVisits {visits}\n')
        print(moves)
        for c, (row, col) in moves:
            gtp_move = coord_to_gtp(row, col)
            gtp_commands.append(f'play {c} {gtp_move}\n')
        gtp_commands.append(f'genmove {gtp_color}\n')
        
        # Print all input commands
        if DEBUG:
            
            print('=== sgf ===')
            print(sgf_data)
            print("=== INPUT TO KATAGO ===")
            for cmd in gtp_commands:
                print_if_debug(cmd, "input")

        # Send all commands
        for cmd in gtp_commands:
            proc.stdin.write(cmd)
        proc.stdin.flush()

        # Read and print stdout in real time
        output = []
        move = 'pass'
        while True:
            line = proc.stdout.readline()
            if not line:  # EOF
                break
            print_if_debug(line, "stdout")
            #print('res2 ')
            if len(line.split('='))==2:
                # Split the line after '=' and strip whitespace
                result = line.split('=')[1].strip()
                if len(result)>0:
                    move = result
                    #print('res1 ',result)
                    break
                #print('res ',result)
            #print('res3 ')
        # Print stderr at the end (for simplicity)
        #stderr_lines = proc.stderr.readlines()
        #for line in stderr_lines:
        #    print_if_debug(line, "stderr")

    finally:
        proc.terminate()
    print(move)
    return jsonify({'move': '= '+move})

if __name__ == '__main__':
    app.run(port=5000)
