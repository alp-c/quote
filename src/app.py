from services.server import QuoteServer
import asyncio, signal

async def main():
    port = 5021 # quote requests will be served at this port
    symbols = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "BNBUSDT", "USDTTRY"]
    quote_server = QuoteServer().set_port(port).set_symbols(symbols).build().start()

    def on_stop_signal():
        """Trigger stopping server when close application signal received"""
        print("stop triggered")
        quote_server.stop()

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, on_stop_signal)

if __name__ == "__main__":
    try:
        print("Application started")
        asyncio.run(main())
    except SystemExit:
        print("Application is closing...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise e #debug