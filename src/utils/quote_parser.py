from models.quote import QuoteRequest, QuoteResponse
import math


class QuoteParser:
    @staticmethod
    def validate_request(json:dict) -> str:
        """Validates parameters in json"""
        
        # check parameters exist and filled
        for param in ["action", "base_currency", "quote_currency", "amount"]:
            if param not in json:
                return f"Missing parameter '{param}'"
            elif json[param] == "":
                return f"Parameter '{param}' is empty"
            
        # check action is valid
        action = json["action"]
        if not (action == "buy" or action == "sell"):
            return f"'{action}' is not valid action"

        # check amount is valid positive finite number
        try:
            amount = float(json["amount"])

            if not math.isfinite(amount) or amount < 0:
                raise ValueError

        except ValueError:
            return f"'{json['amount']}' is not valid amount"
        
        # no error
        return ""

    @staticmethod
    def to_request(json:dict) -> QuoteRequest:
        """Converts json parameters to QuoteRequest model"""
        action = json["action"]
        base_currency = json["base_currency"]
        quote_currency = json["quote_currency"]
        amount = float(json["amount"])
        return QuoteRequest(action, base_currency, quote_currency, amount)
        
    @staticmethod
    def to_response_json(respone: QuoteResponse) -> dict[str, str]:
        """Converts response model to json"""
        return {
            "total": str(respone.total),
            "price" : str(respone.price),
            "currency": respone.currency
		}