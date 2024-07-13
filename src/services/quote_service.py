from typing import List, Dict, Union
from models.quote import QuoteRequest, QuoteResponse
from models.order_book import LimitOrderBook
from services.price_service import OrderBookObserver

class QuoteService(OrderBookObserver):
    """Stores order books in memory and calculates best price for given quote request"""
    def __init__(self):
        self.order_books: Dict[str, LimitOrderBook] = {}
        
    def on_order_book_received(self, order_book:LimitOrderBook):
        self.order_books[order_book.symbol] = order_book
        
    def quote(self, request:QuoteRequest) -> Union[QuoteResponse, str]:
        """Calculates best price for given quote request"""

        symbol = request.get_symbol()
        symbol_reversed = request.get_symbol(reversed=True)

        if symbol in self.order_books:
            order_book = self.order_books[symbol]
            uses_reverse_symbol = False

        elif symbol_reversed in self.order_books:
            order_book = self.order_books[symbol_reversed]
            uses_reverse_symbol = True

        # when given symbol is not exist on order books
        else:
            valid_symbols = list(self.order_books.keys())

            # error message
            return \
                f"Quote requested symbol '{symbol}' or '{symbol_reversed}' is not valid or not configured on watchlist. " + \
                f"Current order book symbols are '{','.join(valid_symbols)}'"

        # current best offers on order book due to action
        if request.action == "buy":
            offers = order_book.asks
        else:
            offers = order_book.bids
        
        # order book depth
        levels = len(offers)

        # aggregated quantity and amount sizes in order book
        total_quantity = 0
        total_volume = 0

        for i in range(levels):
            total_quantity += offers[i].quantity
            total_volume += offers[i].quantity * offers[i].price

            # check at current level reached sufficient amount of quantity to fill request
            if uses_reverse_symbol:
                matched = total_volume >= request.amount
            else:
                matched = total_quantity >= request.amount

            if matched:
                matched_price = offers[i].price

                if uses_reverse_symbol:
                    return QuoteResponse(request.amount / matched_price, matched_price, request.quote_currency)
                else:
                    return QuoteResponse(matched_price * request.amount, matched_price, request.quote_currency)
        
        # error on no match
        return f"Order book is not liquid enough to fill your request. " + \
            f"First {levels} levels covers only {(total_quantity/request.amount)*100}% of your requested amount."