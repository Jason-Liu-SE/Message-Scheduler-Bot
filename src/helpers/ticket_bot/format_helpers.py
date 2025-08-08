def display_stock(stock: int) -> str:
    return "∞" if stock < 0 else "OUT OF STOCK" if stock == 0 else stock
