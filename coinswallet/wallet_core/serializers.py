from rest_framework import serializers
from wallet_core.models import UserPHPWallet, PHPWalletTransaction

__author__ = 'kaushal'


class PHPWalletListSerializer(serializers.ModelSerializer):
    """
    Provide list of accounts for payment recipient list requested
    All, fields are read only
    """
    owner = serializers.ReadOnlyField(source='owner.get_username')
    currency = serializers.CharField(default='PHP')

    class Meta:
        model = UserPHPWallet
        fields = ('id', 'owner', 'balance', 'currency')
        read_only_fields = ('id', 'owner', 'balance', 'currency')


class WalletTransactionSerializer(serializers.ModelSerializer):
    """
    Serialize wallet transactions,
    Read only fields
    """
    direction = serializers.CharField()
    debit_from = serializers.CharField(source='wallet_from.owner.get_username')
    credit_to = serializers.CharField(source='wallet_to.owner.get_username')
    currency = serializers.CharField(default='PHP')

    class Meta:
        model = PHPWalletTransaction
        fields = ('id', 'amount', 'currency', 'direction',
                  'debit_from', 'credit_to', 'created')
        read_only_fields = ('id', 'wallet_from', 'wallet_to',
                            'amount', 'created', 'currency')
