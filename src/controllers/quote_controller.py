from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

from services.quote_service import QuoteService
from models.quote import QuoteRequest, QuoteResponse
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

            if isinstance(quote_response, QuoteResponse):
                response_json = QuoteParser.to_response_json(quote_response)
                return jsonify(response_json), 200
            else:
                return jsonify(quote_response), 400
        
        except BadRequest as e:
            return jsonify(e.description), 400

        except Exception as e:
            return jsonify("Internal Server Error: " + e), 500

    return app