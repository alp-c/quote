import asyncio
from asyncio import Task
from typing import List
from flask import Flask
from services.exchange_service import BinanceSpotWebSocketClient
from services.quote_service import QuoteService
from controllers.quote_controller import create_controller

class QuoteServer:
    """Builds quote service server. Initializes and executes all required services"""
    def __init__(self):
        self.symbols: List[str] = []
        """Watched symbols list. Will be connected given symbols"""

        self.port = 5000
        """HTTP request controller's served port"""

        self.binance_client:BinanceSpotWebSocketClient = None
        """Manages websocket connection to Binance - Spot Markets"""

        self.quote_service:QuoteService = None
        """Stores order books in memory and calculates best price for given quote request"""
        
        self.quote_controller:Flask = None
        """Handles with http requests and redirects to quote service"""

        self.quote_controller_task:Task = None

    def set_symbols(self, symbols: List[str]):
        """Sets watchlist, will connect streams of given symbols"""
        self.symbols = symbols
        return self

    def set_port(self, port:int):
        """Sets http request controller's served port"""
        self.port = port
        return self

    def build(self):
        """Initializes all required services"""

        self.quote_service:QuoteService = QuoteService()
        self.quote_controller:Flask = create_controller(self.quote_service)

        self.binance_client:BinanceSpotWebSocketClient = BinanceSpotWebSocketClient()
        self.binance_client.set_symbols(self.set_symbols)
        self.binance_client.observers.append(self.quote_service)

        return self
    
    def start(self):
        """Connects stock exchange websockets and starts serving quote service"""
        self.binance_client.start()
        self.quote_controller_task = asyncio.create_task(self.quote_controller.run(host="0.0.0.0", port=self.port))
        return self

    def stop(self):
        """Disconnects stock exchange websockets and stops serving quote service"""
        self.binance_client.stop()
        self.quote_controller_task.cancel()
        return self