from dataclasses import dataclass, field
from typing import List

@dataclass
class LimitOrder:
    """Makers' total offer at one price level"""
    price: float
    quantity: float

@dataclass
class LimitOrderBook:
    symbol: str
    bids: List[LimitOrder] = field(default_factory=list)
    asks: List[LimitOrder] = field(default_factory=list)