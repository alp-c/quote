from models.quote import QuoteRequest, QuoteResponse
from models.order_book import LimitOrder, LimitOrderBook
from utils.quote_parser import QuoteParser
from services.quote_service import QuoteService

class TestQuoteService:
    """Tests quote calculations"""

    def setup_method(self):
        """Initializes common variables for tests"""
        order_book = LimitOrderBook(
            symbol="ETHUSDT",
            asks = [
                LimitOrder(2000, 10),
                LimitOrder(2100, 15),
                LimitOrder(2200, 10)],
            bids = [
                LimitOrder(1900, 10),
                LimitOrder(1800, 20),
                LimitOrder(1700, 10)])

        self.quote_service = QuoteService()
        self.quote_service.on_order_book_received(order_book)

    def test_on_order_book_received(self):
        assert "ETHUSDT" in self.quote_service.order_books

    def test_unreceived_symbol(self):
        request = QuoteRequest(action="buy", base_currency="LTC", quote_currency="USDT", amount=1.5)
        response = self.quote_service.quote(request)
        assert isinstance(response, str)
        assert "not valid" in response

    def test_request_1_buy_with_eth(self):
        request = QuoteRequest(action="buy", base_currency="ETH", quote_currency="USDT", amount=1.5)
        response = self.quote_service.quote(request)
        assert isinstance(response, QuoteResponse)
        assert response.total == 3000.0
        assert response.price == 2000.0
        assert response.currency == "USDT"

    def test_request_2_buy_with_usdt(self):
        request = QuoteRequest(action="buy", base_currency="USDT", quote_currency="ETH", amount=500)
        response = self.quote_service.quote(request)
        assert isinstance(response, QuoteResponse)
        assert response.total == 0.25
        assert response.price == 2000.0
        assert response.currency == "ETH"

    def test_request_1_sell_with_eth(self):
        request = QuoteRequest(action="sell", base_currency="ETH", quote_currency="USDT", amount=1.5)
        response = self.quote_service.quote(request)
        assert isinstance(response, QuoteResponse)
        assert response.total == 2850.0
        assert response.price == 1900.0
        assert response.currency == "USDT"

    def test_request_2_sell_with_3800_usdt(self):
        request = QuoteRequest(action="sell", base_currency="USDT", quote_currency="ETH", amount=3800)
        response = self.quote_service.quote(request)
        assert isinstance(response, QuoteResponse)
        assert response.total == 2.0
        assert response.price == 1900.0
        assert response.currency == "ETH"

    def test_request_fill_at_level_2(self):
        request = QuoteRequest(action="buy", base_currency="ETH", quote_currency="USDT", amount=20)
        response = self.quote_service.quote(request)
        assert isinstance(response, QuoteResponse)
        assert response.currency == "USDT"

        # matched ask offer 2 to fill requested amount completely
        # in real life it should be weighted avg price
        # but for simlicity only uses last price level's price that fills request
        assert response.price == 2100.0 
        assert response.total == 42000.0

    def test_unfilled_request(self):
        """Tests buying with 7M $ while top level order book not sufficient to calculate"""
        request = QuoteRequest(action="buy", base_currency="USDT", quote_currency="ETH", amount=7000000)
        response = self.quote_service.quote(request)
        assert isinstance(response, str)
        assert "not liquid" in response