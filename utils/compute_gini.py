def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.agents]
    x = sorted(agent_wealths)
    n = model.num_agents
    B = sum(xi * (n - i) for i, xi in enumerate(x)) / (n * sum(x)) # enumerate(x) takes the list x and returns pairs of (i, xi) for each element. i is the index (starting at 0). xi is the value at that index in the list.
    return 1 + (1 / n) - 2 * B