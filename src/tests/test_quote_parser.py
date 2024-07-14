import pytest
from models.quote import QuoteRequest, QuoteResponse
from utils.quote_parser import QuoteParser

def test_validate_request_success():
    json = {
        "action": "buy",
        "base_currency": "USD",
        "quote_currency": "EUR",
        "amount": "100"
    }
    assert QuoteParser.validate_request(json) == ""

def test_validate_request_missing_param():
    json = {
        "action": "buy",
        "base_currency": "USD",
        "quote_currency": "EUR"
        # Missing amount
    }
    assert QuoteParser.validate_request(json) == "Missing parameter 'amount'"

def test_validate_request_empty_param():
    json = {
        "action": "buy",
        "base_currency": "USD",
        "quote_currency": "EUR",
        "amount": ""
    }
    assert QuoteParser.validate_request(json) == "Parameter 'amount' is empty"

def test_validate_request_invalid_action():
    json = {
        "action": "exchange",
        "base_currency": "USD",
        "quote_currency": "EUR",
        "amount": "100"
    }
    assert QuoteParser.validate_request(json) == "'exchange' is not valid action"

def test_validate_request_invalid_amount():
    json = {
        "action": "buy",
        "base_currency": "USD",
        "quote_currency": "EUR",
        "amount": "invalid_amount"
    }
    assert QuoteParser.validate_request(json) == "'invalid_amount' is not valid amount"

def test_to_request():
    json = {
        "action": "buy",
        "base_currency": "USD",
        "quote_currency": "EUR",
        "amount": "100"
    }
    request = QuoteParser.to_request(json)
    assert isinstance(request, QuoteRequest)
    assert request.action == "buy"
    assert request.base_currency == "USD"
    assert request.quote_currency == "EUR"
    assert request.amount == 100.0

def test_to_response_json():
    response = QuoteResponse(total=150.0, price=1.5, currency="EUR")
    json_response = QuoteParser.to_response_json(response)
    assert json_response == {
        "total": "150.0",
        "price": "1.5",
        "currency": "EUR"
    }