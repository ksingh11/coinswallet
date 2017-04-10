# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time

from django.db import transaction as db_transaction
from django.db.models import F, Value, When, Case, CharField, Q
from wallet_core.constants import MIN_TIME_DIFF_FOR_SIMILAR_TXN
from wallet_core.exceptions import SuspiciousRequest, InsufficientBalance, \
    TransactionFailed
from wallet_core.models import PHPWalletTransaction, UserPHPWallet
from django.utils.translation import ugettext_lazy as _
from math import ceil
from wallet_core.modules import GetRequestPaginator
from wallet_core.serializers import PHPWalletListSerializer, \
    WalletTransactionSerializer


class WalletTransaction:
    """
    methods for transaction related with wallet
    """
    def __init__(self):
        pass

    @staticmethod
    def inter_wallet_payment(request_user, wallet_from, wallet_to, amount):
        """
        Inter-wallet payment transfer module,
        transfers specified amount from one PHPWallet to other,
        also, records the transaction.

        Validations:
        - Check if provided wallets are two distinct wallets
        - Check if wallet to credited has sufficient fund
        - Check if request user is owner of wallet to be debited
        - Check if any case of suspicious request

        Exceptions: SuspiciousRequest, InsufficientBalance, TransactionFailed

        :param request_user: AUTH_USER_MODEL model's instance, the request user
        :param wallet_from: UserPHPWallet model's instance, wallet to debited
        :param wallet_to: UserPHPWallet model's instance, wallet to credit
        :param amount: Float value, amount to be transferred
        :return: Boolean True, other wise raise some exception
        """

        # Check if both wallets are not same
        if wallet_from == wallet_to:
            raise SuspiciousRequest(_('Cannot transfer payment to own wallet'))

        # Check for suspicious transaction,
        # If similar transaction is being done within some defined time-frame,
        # similar transaction: same amount between same two wallets
        prev_transaction = PHPWalletTransaction.objects\
            .filter(wallet_from=wallet_from, wallet_to=wallet_to,
                    amount=amount).values('created')

        if prev_transaction:
            prev_transaction = prev_transaction[0]
            time_now = int(time.time())
            transaction_time = int(time.mktime(prev_transaction['created']
                                               .timetuple()))

            if (time_now - transaction_time) < MIN_TIME_DIFF_FOR_SIMILAR_TXN:
                time_remaining_min = \
                    int(ceil((MIN_TIME_DIFF_FOR_SIMILAR_TXN -
                              (time_now - transaction_time)) / 60.0))

                raise SuspiciousRequest(_('Same transaction restricted twice, '
                                          'please retry after %d minutes')
                                        % time_remaining_min)

        # Check if request user is owner of wallet to be debited
        if not wallet_from.owner == request_user:
            raise SuspiciousRequest(_('Unauthorised Access'))

        # Execute transaction
        try:
            with db_transaction.atomic():

                # Check if there is sufficient fund in wallet to debit
                wallet_from.refresh_from_db()
                if wallet_from.balance < amount:
                    raise InsufficientBalance(_('Insufficient Balance'))

                # Update balance after withdrawal, in wallet to be debited
                UserPHPWallet.objects.filter(id=wallet_from.id)\
                    .update(balance=F('balance') - amount)

                # Update balance after credit, in wallet to be credited
                UserPHPWallet.objects.filter(id=wallet_to.id)\
                    .update(balance=F('balance') + amount)

                # record the transaction to PHPWalletTransaction model
                PHPWalletTransaction.objects.create(wallet_from=wallet_from,
                                                    wallet_to=wallet_to,
                                                    amount=amount)
        except InsufficientBalance, e:
            raise InsufficientBalance(e.message)

        except Exception:
            raise TransactionFailed(_('Transaction failed, something wrong'))

        return True

    @staticmethod
    def get_transaction_history(wallet, page_requested, page_size):
        """
        get transaction history of requested wallet
        :param wallet: UserPHPWallet instance
        :param page_requested: Integer
        :param page_size: Integer
        :return:
        transaction_history: serialized list of transactions of wallet
        meta_data: pagination information, helpful in subsequent calls
        """
        # TODO: Implement caching, to reduce direct queries to DB

        # query all transactions where 'wallet' is 'wallet_from' or 'wallet_to'
        # then, use 'annotate' to mark transactions 'incoming' or 'outgoing',
        # using 'Case expression' of DB query,
        # also, order transaction in chronological order
        queryset = PHPWalletTransaction.objects\
            .select_related('wallet_from__owner', 'wallet_to__owner')\
            .filter(Q(wallet_from=wallet) | Q(wallet_to=wallet))\
            .annotate(direction=Case(When(wallet_from=wallet,
                                          then=Value('outgoing')),
                                     default=Value('incoming'),
                                     output_field=CharField()))

        # paginate queryset
        sub_queryset, meta_data = \
            GetRequestPaginator(queryset, page_requested, page_size).paginate()

        # serialize queryset
        transaction_list = \
            WalletTransactionSerializer(sub_queryset, many=True).data

        return transaction_list, meta_data


class WalletController:
    """
    methods for view, update wallet details
    """
    def __init__(self):
        pass

    @staticmethod
    def get_all_php_wallets(page_requested, page_size):
        """
        Paginated method to return list of all accounts
        :param page_requested: Integer
        :param page_size: Integer
        :return:
        accounts_list: serialized account list
        meta_data: pagination information, helpful in subsequent calls
        """
        # TODO: Implement caching, to reduce direct queries to DB
        queryset = UserPHPWallet.objects.select_related('owner').all()

        # paginate queryset
        sub_queryset, meta_data = \
            GetRequestPaginator(queryset, page_requested, page_size).paginate()

        # serialize queryset to be sent to client
        accounts_list = PHPWalletListSerializer(sub_queryset, many=True).data

        return accounts_list, meta_data
