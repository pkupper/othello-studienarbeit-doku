def alphabeta(state, depth, alpha, beta, heuristic):
    if(state.game_over):
        return get_winner(state)
    if(depth <= 0):
        return heuristic(state)

    if state.turn == WHITE:
        # maximizing
        utility = -math.inf
    else:
        # minimizing
        utility = math.inf
        
    for move in get_possible_moves(state, state.turn):
        tmp_state = make_move(copy.deepcopy(state), move[0], move[1])
        tmp_utility = alphabeta(tmp_state, depth - 1, alpha, beta, heuristic)
        
        if state.turn == WHITE:
            # maximizing
            utility = max(utility, tmp_utility)
            alpha = max(alpha, utility)
        else:
            # minimizing
            utility = min(utility, tmp_utility)
            beta = min(beta, utility)
        if(alpha >= beta):
            break # alphabeta pruning
    return utility