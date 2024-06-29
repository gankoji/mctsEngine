# Trying to build a basic chess interaction model here. 
import chess
import chess.syzygy
import math
import random
import time

tablebase = chess.syzygy.open_tablebase('./3-4-5')

piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
colors = [chess.WHITE, chess.BLACK]

class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state  # Game state (e.g., board representation)
        self.parent = parent
        self.move = move    # Move that led to this state
        self.children = []  # List of child nodes
        self.wins = 0
        self.visits = 0

def total_number_of_pieces(board):
    n = 0
    for c in colors:
        for p in piece_types:
            n += len(board.pieces(p,c))

    return n

def uct(node):
    """Upper Confidence Bound for Trees (UCT) score."""
    if node.visits == 0:
        return float("inf")
    return node.wins / node.visits + 2 * (2 * math.log(node.parent.visits) / node.visits) ** 0.5

def select(node):
    """Select a promising child node to explore."""
    return max(node.children, key=uct)

def expand(node):
    """Add children for legal moves (using python-chess)."""
    for move in node.state.legal_moves:
        child_state = node.state.copy()
        child_state.push(move)
        node.children.append(Node(child_state, node, move))
    return random.choice(node.children)

def simulate(node):
    """Play a random game (using python-chess)."""
    state = node.state.copy()
    while not state.is_game_over():
        if total_number_of_pieces(state) <= 5:
            res = tablebase.probe_wdl(state)
            if res == 2:
                return 1
            elif res == -2:
                return 0
            else:
                return 0.5
        move = random.choice(list(state.legal_moves))
        state.push(move)
    result = state.result()
    return 1 if result == "1-0" else 0 if result == "0-1" else 0.5  # Win, loss, or draw

def backpropagate(node, result):
    """Update visit count and wins along the path."""
    while node is not None:
        node.visits += 1
        node.wins += result
        node = node.parent

def is_terminal(board):
    if board.outcome():
        return True
    return False

def mcts(board, num_iterations):
    """Main MCTS loop."""
    root_node = Node(board)

    for _ in range(num_iterations):
        node = root_node
        while node.children:
            node = select(node)
        if node.visits > 0 and not is_terminal(node.state):
            node = expand(node)
        result = simulate(node)
        backpropagate(node, result)

    #return max(root_node.children, key=lambda c: c.visits).move  # Choose most visited move
    best_move = max(root_node.children, key=lambda c: c.visits).move
    return best_move

print("Attempting to play with the MCTS engine.")
board = chess.Board()
times = []

for i in range(5):
    start = time.time()
    next_move = mcts(board, 50)
    stop = time.time() - start
    times.append(stop)

avg = sum(times)/len(times)
print("Average time per move: ", avg)
print(next_move)
