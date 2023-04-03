"""
Exceptions for MarketWatch

This module contains the set of MarketWatch's exceptions.

Classes:
    MarketWatchException
    MarketWatchGameException
"""

class MarketWatchException(Exception):
    """
    Base exception for MarketWatch

    Attributes:
        message (str): Exception message

    """
    def __init__(self, message):
        self.message = f"MarketWatchException: {message}"


class MarketWatchGameException(Exception):
    """
    Exception for MarketWatchGame

    Attributes:
        message (str): Exception message
    """
    def __init__(self, message):
        self.message = f"MarketWatchException: {message}"
