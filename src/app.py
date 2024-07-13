from services.server import QuoteServer
import asyncio

async def main():
    port = 5021  # Quote requests will be served at this port
    symbols = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "BNBUSDT", "USDTTRY"]
    quote_server = QuoteServer().set_port(port).set_symbols(symbols).build()

    await quote_server.start()

    # Keep the main function running to handle shutdown on Ctrl+C
    try:
        while True:
            await asyncio.sleep(1)

    except:
        await quote_server.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise e  # Debug