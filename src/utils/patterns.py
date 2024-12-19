def find_support_resistance(prices):
    levels = []
    window = 5

    for i in range(window, len(prices) - window):
        if is_support(prices, i, window):
            levels.append(("support", prices[i]))
        if is_resistance(prices, i, window):
            levels.append(("resistance", prices[i]))

    return levels


def is_support(prices, i, window):
    # Support level detection
    pass
