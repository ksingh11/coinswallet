from coinswallet.settings import ACCESS_TOKEN_EXPIRE_SECONDS, \
    TIME_LIMIT_FOR_SIMILAR_TRANSACTION

__author__ = 'kaushal'

# Constants definitions to used by wallet_core app.
# Define constants here:

# Set value for minimum time difference required to allow same transaction
# Limiting to 10 minutes or, if access token get expired prior to 10 minutes
if ACCESS_TOKEN_EXPIRE_SECONDS < TIME_LIMIT_FOR_SIMILAR_TRANSACTION:
    MIN_TIME_DIFF_FOR_SIMILAR_TXN = ACCESS_TOKEN_EXPIRE_SECONDS
else:
    MIN_TIME_DIFF_FOR_SIMILAR_TXN = TIME_LIMIT_FOR_SIMILAR_TRANSACTION
