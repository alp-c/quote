from abc import ABC, abstractmethod
from models.order_book import LimitOrder, LimitOrderBook

class ExchangeWebSocketMessageParser(ABC):
    """Converts received raw json messages to models"""
    
    @abstractmethod
    def is_order_book(self, message:dict) -> bool:
        """Checks wether received message is order book data or not"""
        pass

    @abstractmethod
    def convert_order_book(self, message:dict) -> LimitOrderBook:
        """Converts received json message to order book model"""
        pass

class BinanceSpotWebSocketMessageParser(ExchangeWebSocketMessageParser):
    """Converts received raw json messages to models for Binance Spot markets"""

    def _get_stream_name(self, message: dict) -> str:
        """Gets stream name from stream message"""
        return message['stream']
    
    def _get_stream_data(self, message: dict) -> dict:
        """Gets price data json from stream message"""
        return message['data']

    def is_order_book(self, message: dict) -> bool:
        return "depth" in self._get_stream_name(message)
    
    def convert_order_book(self, message: dict) -> LimitOrderBook:
        stream_name = self._get_stream_name(message)
        stream_data = self._get_stream_data(message)

        # example: converts stream name 'ethusdt@depth5@100ms' to symbol 'ETHUSDT'
        symbol = stream_name.split('@')[0].upper()
        
        bids = [LimitOrder(float(price), float(quantity)) for price, quantity in stream_data.get("bids", [])]
        asks = [LimitOrder(float(price), float(quantity)) for price, quantity in stream_data.get("asks", [])]
        
        return LimitOrderBook(symbol, bids, asks)