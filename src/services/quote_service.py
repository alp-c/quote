from typing import List, Dict, Union
from models.quote import QuoteRequest, QuoteResponse
from models.order_book import LimitOrder, LimitOrderBook
from services.price_service import OrderBookObserver

class QuoteService(OrderBookObserver):
    """Stores order books in memory and calculates best price for given quote request"""
    def __init__(self):
        self.order_books: Dict[str, LimitOrderBook] = {}
        
    def on_order_book_received(self, order_book:LimitOrderBook):
        self.order_books[order_book.symbol] = order_book

    @staticmethod
    def _get_total_quantity(orders: List[LimitOrder])-> float:
        """Total quantity in orders"""
        return sum(order.quantity for order in orders)
    
    @staticmethod
    def _get_total_volume(orders: List[LimitOrder])-> float:
        """Total quantity*price of orders"""
        return sum(order.price * order.quantity for order in orders)
    
    @staticmethod
    def _get_weighted_avg_price(orders: List[LimitOrder])-> float:
        """Avg filled price"""
        total_quantity = QuoteService._get_total_quantity(orders)
        total_volume = QuoteService._get_total_volume(orders)

        if total_quantity == 0:
            return 0

        return total_volume / total_quantity

        
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

        # aggregated quantity and amount sizes completely covered request
        is_fill_completed = False

        # matched price levels that fill request
        filled_orders: List[LimitOrder] = []

        for i in range(levels):
            total_quantity += offers[i].quantity
            total_volume += offers[i].quantity * offers[i].price

            # when use reversed symbol fill calcuations based on volume (quantity*price)
            if uses_reverse_symbol:
                # check at current level reached sufficient amount of volume (quantity*price) to fill request
                is_fill_completed = total_volume >= request.amount

                if is_fill_completed:
                    # last required partial volume to complete request
                    volume_left = request.amount - QuoteService._get_total_volume(filled_orders)

                    # last required quantity to complete request
                    quantity_left = volume_left / offers[i].price

                    # current last price level partially added
                    filled_orders.append(LimitOrder(offers[i].price, quantity_left))

                else:
                    # current price level completely added
                    filled_orders.append(offers[i])

            # when use standard symbol fill calculations based on quantity
            else:
                # check at current level reached sufficient amount of quantity to fill request
                is_fill_completed = total_quantity >= request.amount

                if is_fill_completed:
                    # last required partial quantity to complete request
                    quantity_left = request.amount - QuoteService._get_total_quantity(filled_orders)

                    # current last price level partially added
                    filled_orders.append(LimitOrder(offers[i].price, quantity_left))

                else:
                    # current price level completely added
                    filled_orders.append(offers[i])


            if is_fill_completed:
                # avg fill price of filled orders that cover request
                avg_fill_price = QuoteService._get_weighted_avg_price(filled_orders)

                # total volume of filled orders that cover request
                total_fill_volume = QuoteService._get_total_volume(filled_orders)

                # total quantity amount of filled orders that cover request
                total_fill_quantity = QuoteService._get_total_quantity(filled_orders)

                if uses_reverse_symbol:
                    return QuoteResponse(total_fill_quantity, avg_fill_price, request.quote_currency)
                else:
                    return QuoteResponse(total_fill_volume, avg_fill_price, request.quote_currency)
        
        # error on no match
        return f"Order book is not liquid enough to fill your request. "