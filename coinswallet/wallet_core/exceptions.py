__author__ = 'kaushal'

# Define custom exceptions classes here.


class SuspiciousRequest(Exception):
    """
    Custom exception to be used in case of any suspicious request
    """
    pass


class InsufficientBalance(Exception):
    """
    Custom exception to be used in case there isn't sufficient fun.
    """
    pass


class TransactionFailed(Exception):
    """
    Exception for failed transaction due to any unexpected reason
    """
    pass
