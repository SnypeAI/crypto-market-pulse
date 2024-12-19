def find_support_resistance(prices, window=5):
    levels = []
    
    for i in range(window, len(prices) - window):
        if is_support(prices, i, window):
            levels.append(('support', prices[i]))
        if is_resistance(prices, i, window):
            levels.append(('resistance', prices[i]))
    
    return levels

def is_support(prices, i, window):
    current = prices[i]
    for j in range(i - window, i + window + 1):
        if j != i and prices[j] < current:
            return False
    return True

def is_resistance(prices, i, window):
    current = prices[i]
    for j in range(i - window, i + window + 1):
        if j != i and prices[j] > current:
            return False
    return True