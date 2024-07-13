from flask import Flask, request, jsonify
from services.quote_service import QuoteService
from utils.quote_parser import QuoteParser

def create_controller(quote_service:QuoteService) -> Flask:
    """Creates controller that handles http request and redirects to quote service"""

    app = Flask(__name__)
    service = quote_service

    @app.post('/quote')
    def quote():
        """Calculates best price for given QuoteRequest"""
        try:
            request_json = request.get_json()

            error_message = QuoteParser.validate_request(request_json)
            error_exist = error_message != ""

            # bad request
            if error_exist:
                return jsonify(error_message), 400
            
            quote_request = QuoteParser.to_request(request_json)
 
            quote_response = service.quote(quote_request)
            
            response_json = QuoteParser.to_response_json(quote_response)
            
            return jsonify(response_json), 200
        except Exception as e:
            return jsonify("Internal Server Error"), 500
        
    @app.get('/test')
    def test():
        return jsonify("hello"), 200

    return app