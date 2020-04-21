def alphabeta(state, alpha, beta, heuristic):
    if(state.game_over):
        return utility(state, state.turn)
    if state.turn == WHITE:
        # maximizing
        utility = -math.inf
    else:
        # minimizing
        utility = math.inf  
    for move in get_possible_moves(state, state.turn):
        tmp_state = make_move(copy.deepcopy(state), move)
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
            break # alphabeta pruning
    return utility