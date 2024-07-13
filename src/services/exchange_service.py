import asyncio, websockets
from abc import ABC, abstractmethod
from websockets import WebSocketClientProtocol
from asyncio import Task
from typing import List
from services.price_service import OrderBookObserver
from utils.exchange_parser import ExchangeWebSocketMessageParser, BinanceSpotWebSocketMessageParser

class ExchangeWebSocketClient(ABC):
    """Manages websocket connection to stock exchange"""

    def __init__(self, parser:ExchangeWebSocketMessageParser):
        self.parser = parser
        """JSON message to model converter"""

        self.symbols: List[str] = []
        """List of watched symbol names"""

        self.observers: List[OrderBookObserver] = []
        """List of observers of order book events"""

        self.websocket: WebSocketClientProtocol = None
        """Client connection"""

        self.connection_retry_interval = 5
        """Connection retry interval in seconds"""

        self.send_ping_periodically = False
        """Ping interval in minutes"""

        self.ping_interval = 1
        """Ping interval in minutes"""

        self.ping_task: Task = None
        """Task for sending pings to notify stock exchange to keep connection open"""

        self.listen_task: Task = None
        """Task for listening to WebSocket messages"""

        self.stop_event = asyncio.Event()
        """Event to signal stopping the WebSocket connection"""

    def set_symbols(self, symbols: List[str]):
        """Sets list of watched symbols. Connects only streams of specified symbol names"""
        self.symbols = symbols

    @abstractmethod
    def get_uri(self) -> str:
        """Gets uri adress to connect socket"""
        pass

    async def _connect(self):
        while True:
            try:
                self.websocket = await websockets.connect(self.get_uri())
                print("Connected to WebSocket")
                
                if self.ping_task:
                    self.ping_task.cancel()
                
                self.ping_task = asyncio.create_task(self._send_ping())
                break

            except websockets.ConnectionClosedError as e:
                print(f"Connection error: {e}. Retrying in {self.connection_retry_interval} seconds...")
                await asyncio.sleep(self.connection_retry_interval)

            except websockets.InvalidURI as e:
                print("Invalid URI")
                break



    async def _listen(self):
        """Receives and processes messages from websocket"""
        while not self.stop_event.is_set():
            try:
                message = await self.websocket.recv()
                json = json.loads(message)
                self.on_message(json)
            except websockets.ConnectionClosedError:
                print("Connection closed, reconnecting...")
                await self._connect()
            except websockets.WebSocketException as e:
                print(f"WebSocket error: {e}. Reconnecting...")
                await self._connect()
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    async def _send_ping(self):
        while not self.stop_event.is_set():
            try:
                await self.websocket.ping()
                await asyncio.sleep(self.ping_interval * 60) 
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"An error occurred while sending ping: {e}")

    def on_message(self, message):
        """Executed each time on json message received. Converts data and notifies to listeners"""

        if self.parser.is_order_book(message):
            order_book = self.parser.convert_order_book(message)

            for observer in self.observers:
                observer.on_order_book_received(order_book)

    async def start(self):
        """Starts websocket connection and receives datas"""

        # reset stop event
        self.stop_event = asyncio.Event()

        if len(self.symbols) == 0:
            raise ValueError("'symbols' must not be empty to connect socket")
        else:
            await self._connect()
            self.listen_task = asyncio.create_task(self._listen())

    async def stop(self):
        """Stops the WebSocket connection and cleans up tasks"""
        self.stop_event.set()

        if self.websocket:
            await self.websocket.close()

        if self.listen_task:
            self.listen_task.cancel()

        if self.ping_task:
            self.ping_task.cancel()


class BinanceSpotWebSocketClient(ExchangeWebSocketClient):
    """Manages websocket connection to Binance - Spot Markets"""
    def __init__(self):
        super().__init__(BinanceSpotWebSocketMessageParser())
        self.send_ping_periodically = True
        self.ping_interval = 3

    def get_uri(self) -> str:
        depth = 5 # partial order book depth
        interval = "100ms" # order book receive period
        stream_names = [f"{symbol.lower()}@depth{depth}@{interval}" for symbol in self.symbols]
        return f"wss://stream.binance.com:9443/stream?streams={'/'.join(stream_names)}"

    def on_message(self, message):
        # Custom handling of the message
        stream = message['stream']
        data = message['data']
        print(f"Custom handling of message from {stream}: {data}")


"""
# Usage example
symbols = ["btcusdt", "ethusdt"]
client = BinanceSpotWebSocketClient()
client.set_symbols(symbols)
asyncio.run(client.start())
"""