## Description
A web service offering real-time digital currency trade quotes using WebSocket order book data from Binance.
You can learn average price of 

## Architecture

![Architecture](doc/architecture.png)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/alp-c/quote.git
    cd quote
    ```

2. (Optional) Create and activate a virtual environment:
    ```bash
    python -m venv env
    ```
    on windows
    ```
    env\Scripts\activate
    ```
    on linux
    ```
    source env/bin/activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Current configuration (can be changed at src/app.py)
```python
# Quote requests will be served at this port
port = 5021  

# This symbols' partial order book data will be listened from binance spot web-socket
# and can be used to make quote request
symbols = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "BNBUSDT", "USDTTRY"]
```
Start service
```bash
python src/app.py
```
at another terminal window send request to service (tested and works on windows)
```bash
curl -X POST http://localhost:5021/quote -H "Content-Type: application/json" -d "{\"action\": \"buy\", \"base_currency\": \"ETH\", \"quote_currency\": \"USDT\", \"amount\": \"1.5\"}"
```
Received response
```json
{"currency":"USDT","price":"3185.6","total":"4778.4"}
```

### Endpoints: POST /quote

#### Request

- **action** (String): Either "buy" or "sell"
- **base_currency** (String): The currency to be bought or sold
- **quote_currency** (String): The currency to quote the price in
- **amount** (String): The amount of the base currency to be traded

#### Response

- **total** (String): Total quantity of quote currency needed or received
- **price** (String): The per-unit cost of the base currency
- **currency** (String): The quote currency


## Executing Tests
at current repository folder just run
```bash
pytest
```
unit test results
![Architecture](doc/tests.png)

Tested on Python 3.11.4 and Python 3.9.17