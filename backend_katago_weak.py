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
import random

def is_gtp_move(s):
    # Matches one or two letters (skipping 'I'), followed by one or two digits
    # For standard Go, column is A-H,J-T (skips I), row is 1-19
    return re.fullmatch(r'[A-HJ-T][A-HJ-T]?\d{1,2}', s) is not None

app = Flask(__name__)

# Set this to False to disable printing KataGo input/output
DEBUG = False

def coord_to_gtp(row, col):
    # row and col are 0-based, top-left is (0,0)
    # GTP columns: A=0, B=1, ..., H=7, J=8 (skips I), ..., T=18
    # GTP rows: 1=bottom, 19=top (if (0,0) is top-left, need to invert row)
    # So: GTP column is col, GTP row is 19 - row
    # NOTE: If your moves are (row, col) with row=0 at top, this is correct:
    gtp_col = chr(ord('A') + col + (1 if col >= 8 else 0))  # Skip 'I'
    gtp_row = row + 1  # If row is 0-based, top-left is (0,0), and you want 1-based at bottom
    # If you find the moves are mirrored, try gtp_row = 19 - row
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

def get_policy_pick_move(proc, gtp_commands, temperature=1):
    gtp_commands.append('kata-analyze interval 1\n')
    for cmd in gtp_commands:
        proc.stdin.write(cmd)
    #proc.stdin.flush()
    # Print all input commands
    if DEBUG:
        #print('=== sgf ===')
        #print(sgf_data)
        print("=== INPUT TO KATAGO ===")
        for cmd in gtp_commands:
            print_if_debug(cmd, "input")

    proc.stdin.flush()
    policy = {}
    k=0
    stop=False
    while True:
        line1 = proc.stdout.readline()
        if not line1:
            break
        print_if_debug(line1, "stdout")
        if line1.startswith('info move '):
            for line in line1.split('info move'):
                parts = line.split()
                if parts:
                    move = parts[0]
                    # Find the 'prior' field and its value
                    prior_idx = parts.index('prior') + 1 if 'prior' in parts else -1
                    if prior_idx != -1 and prior_idx < len(parts):
                        try:
                            prior = float(parts[prior_idx])
                            policy[move] = prior
                        except (ValueError, IndexError):
                            pass
                    k+=1
                    #print("K  = ",k)
                    if k >= 1000:  # Stop after collecting 20 moves
                        stop=True
                        break
        if (stop):
            break
        #elif line.startswith('='):
        #    break
    if not policy:
        return 'pass'
    # Apply temperature
    weights = [policy[move] ** (1.0 / temperature) for move in policy]
    total = sum(weights)
    weights = [w / total for w in weights]
    print(policy.keys(),weights)
    return random.choices(list(policy.keys()), weights=weights)[0]

def ensure_color_turn(moves, desired_color):
    opposite_color = 'w' if desired_color == 'b' else 'b'
    # Find all indices of moves with the opposite color
    indices = [i for i, (c, _) in enumerate(moves) if c == opposite_color]
    if not indices:
        # No move of opposite color found; can't avoid dummies, but you asked to avoid them
        return moves
    last_idx = indices[-1]
    # If the last move is not already the opposite color
    if last_idx != len(moves) - 1:
        move = moves.pop(last_idx)
        moves.append(move)
    return moves

@app.route('/next-move', methods=['POST'])
def next_move():
    sgf_data = request.json['sgf']
    color = request.json.get('color', 'black').lower()
    gtp_color = 'b' if color.startswith('b') else 'w'
    strength = int(request.json.get('strength', 10))
    visits = 2**strength  # Adjust as needed

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
            # Convert stone to (row, col)
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
    
    # Ensure the last move is the opposite color of what we want to play
    #print(moves)
    moves = ensure_color_turn(moves, gtp_color)
    #print(moves)
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
        # Send all moves except dummy passes (where row=col=-1)
        for c, (row, col) in moves:
            if row == -1 and col == -1:
                # Skip dummy passes added by ensure_color_turn
                continue
            gtp_move = coord_to_gtp(row, col)
            gtp_commands.append(f'play {c} {gtp_move}\n')
        

        # Send all commands


        # Use policy pick to get the next move
        temperature=1/1.7**(strength-5)
        move = get_policy_pick_move(proc, gtp_commands,temperature)

        # Print stderr at the end (for simplicity)
        #stderr_lines = proc.stderr.readlines()
        #for line in stderr_lines:
        #    print_if_debug(line, "stderr")

    finally:
        proc.terminate()

    # Return the move in GTP format (e.g., "= M5")
    return jsonify({'move': '= ' + move})

if __name__ == '__main__':
    app.run(port=5000)
