def get_emoji(last_price, ma):
    if last_price < ma:
        return '📈'
    else:
        return '📉'