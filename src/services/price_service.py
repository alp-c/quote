from abc import ABC, abstractmethod
from models.order_book import LimitOrderBook

class OrderBookObserver(ABC):
    """Listens `LimitOrderBook` events"""
    
    @abstractmethod
    def on_order_book_received(self, order_book: LimitOrderBook):
        """Executed action when new order book data received"""
        pass