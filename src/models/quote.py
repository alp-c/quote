from dataclasses import dataclass

@dataclass
class QuoteRequest:
    action: str
    base_currency: str
    quote_currency: str
    amount: str

    def get_symbol(self, reversed=False):
       symbol = self.quote_currency + self.base_currency if reversed \
        else self.base_currency + self.quote_currency
       
       return symbol.upper()
    

@dataclass
class QuoteResponse:
    total: str
    price: str
    currency: str