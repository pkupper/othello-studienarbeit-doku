def alphabeta(state, alpha, beta, heuristic):
    if(state.game_over):
        return get_utility(state, state.turn)
    if state.turn == WHITE:
        # maximizing
        utility = -math.inf
    else:
        # minimizing
        utility = math.inf  
    for move in state.possible_moves:
        tmp_state = make_move(state, move)
        tmp_utility = alphabeta(tmp_state, alpha, beta, heuristic)
        if state.turn == WHITE:
            # maximizing
            utility = max(utility, tmp_utility)
            alpha = max(alpha, utility)
        else:
            # minimizing
            utility = min(utility, tmp_utility)
            beta = min(beta, utility)
        if(alpha >= beta):
            break # alpha-beta pruning
    return utility