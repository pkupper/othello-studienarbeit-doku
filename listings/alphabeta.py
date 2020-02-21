def alphabeta_max(state, alpha, beta, depth):
    global alphabeta_best_move
    if state.game_over:
        return terminal_utility(state)
    if depth >= ALPHABETA_DEPTH_LIMIT:
        return heuristic_utility(state)
    max_utility = -math.inf
    for move in state.get_possible_moves():
        tmp_state = copy.deepcopy(state)
        tmp_state.move(move[0], move[1])
        tmp_utility = alphabeta_min(tmp_state, alpha, beta, depth + 1)
        if tmp_utility > max_utility:
            max_utility = tmp_utility
            if depth == 0:
                alphabeta_best_move = move
        if max_utility >= beta:
            return max_utility
        alpha = max(alpha, max_utility)
    return max_utility

def alphabeta_min(state, alpha, beta, depth):
    global alphabeta_best_move
    if state.game_over:
        return -terminal_utility(state)
    if depth >= ALPHABETA_DEPTH_LIMIT:
        return -heuristic_utility(state)
    min_utility = math.inf
    for move in state.get_possible_moves():
        tmp_state = copy.deepcopy(state)
        tmp_state.move(move[0], move[1])
        tmp_utility = alphabeta_max(tmp_state, alpha, beta, depth + 1)
        if tmp_utility < min_utility:
            min_utility = tmp_utility
            if depth == 0:
                alphabeta_best_move = move
        if min_utility <= alpha:
            return min_utility
        beta = min(beta, min_utility)
    return min_utility