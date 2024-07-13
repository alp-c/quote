import asyncio
from typing import List
from flask import Flask
from services.exchange_service import BinanceSpotWebSocketClient
from services.quote_service import QuoteService
from controllers.quote_controller import create_controller
from concurrent.futures import ThreadPoolExecutor

class QuoteServer:
    """Builds quote service server. Initializes and executes all required services"""
    def __init__(self):
        self.symbols: List[str] = []
        """Watched symbols list. Will be connected given symbols"""

        self.port = 5000
        """HTTP request controller's served port"""

        self.binance_client: BinanceSpotWebSocketClient = None
        """Manages websocket connection to Binance - Spot Markets"""

        self.quote_service: QuoteService = None
        """Stores order books in memory and calculates best price for given quote request"""

        self.quote_controller: Flask = None
        """Handles with HTTP requests and redirects to quote service"""

        self.quote_controller_executor = ThreadPoolExecutor(max_workers=1)

    def set_symbols(self, symbols: List[str]):
        """Sets watchlist, will connect streams of given symbols"""
        self.symbols = symbols
        return self

    def set_port(self, port: int):
        """Sets HTTP request controller's served port"""
        self.port = port
        return self

    def build(self):
        """Initializes all required services"""

        self.quote_service: QuoteService = QuoteService()
        self.quote_controller: Flask = create_controller(self.quote_service)

        self.binance_client: BinanceSpotWebSocketClient = BinanceSpotWebSocketClient()
        self.binance_client.set_symbols(self.symbols)
        self.binance_client.observers.append(self.quote_service)

        return self

    async def start(self):
        """Connects stock exchange websockets and starts serving quote service"""
        print("Server started")
        await self.binance_client.start()
        loop = asyncio.get_event_loop()
        loop.run_in_executor(self.quote_controller_executor, self.quote_controller.run, "0.0.0.0", self.port)
        return self

    async def stop(self):
        """Disconnects stock exchange websockets and stops serving quote service"""
        self.binance_client.stop()
        self.quote_controller_executor.shutdown(wait=False)
        print("Server stopped")
        return self