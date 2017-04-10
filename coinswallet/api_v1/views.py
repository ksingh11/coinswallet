# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from coinswallet.settings import DEFAULT_GET_RESPONSE_PER_PAGE, \
    MAX_GET_RESPONSE_PER_PAGE
from oauth2_provider.ext.rest_framework import TokenHasScope, \
    OAuth2Authentication
from rest_framework import status
from rest_framework.authtoken.views import APIView
from rest_framework.response import Response
from wallet_core.exceptions import SuspiciousRequest, InsufficientBalance, \
    TransactionFailed
from wallet_core.models import UserPHPWallet
from wallet_core.views import WalletTransaction, WalletController


class AccountsAPI(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['view']

    def get(self, request):
        """
        Retrieves list of all registered wallets (accounts)
        query_string:
        - page: page number of paginated response
        - per_page: number of entries in one page
        return: requested account's list, meta data for pagination
        """
        get_params = request.GET

        # validate page number requested
        page_requested = get_params.get('page', '')
        try:
            page_requested = int(page_requested)
        except ValueError:
            response = {
                'success': False,
                'message': 'page parameter invalid'
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

        # validate page size requested
        page_size = get_params.get('per_page', DEFAULT_GET_RESPONSE_PER_PAGE)
        try:
            page_size = int(page_size)
            if page_size > MAX_GET_RESPONSE_PER_PAGE:
                raise ValueError
        except ValueError:
            response = {
                'success': False,
                'message': 'per_page parameter invalid'
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

        # Retrieve paginated account list, for requested page
        accounts_list, meta_data = \
            WalletController.get_all_php_wallets(page_requested, page_size)
        return Response(status=status.HTTP_200_OK,
                        data={'success': True,
                              'message': 'Account list retrieved',
                              'accounts': accounts_list, 'meta': meta_data})


class PaymentAPI(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['view', 'transact']

    def get(self, request):
        """
        Retrieves the list of all transaction, both outbound and inbound
        query_string:
        - page: page number of paginated response
        - per_page: number of entries in one page
        :return: list of transaction in chronological order
        """
        get_params = request.GET

        # validate page number requested
        page_requested = get_params.get('page', '')
        try:
            page_requested = int(page_requested)
        except ValueError:
            response = {
                'success': False,
                'message': 'page parameter invalid'
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

        # validate page size requested
        page_size = get_params.get('per_page', DEFAULT_GET_RESPONSE_PER_PAGE)
        try:
            page_size = int(page_size)
            if page_size > MAX_GET_RESPONSE_PER_PAGE:
                raise ValueError
        except ValueError:
            response = {
                'success': False,
                'message': 'per_page parameter invalid'
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

        try:
            wallet = UserPHPWallet.objects.get(owner=request.user)
        except UserPHPWallet.DoesNotExist:
            response = {
                'success': False,
                'message': 'per_page parameter invalid'
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

        # Retrieve requested transaction details
        transaction_list, meta_data = WalletTransaction\
            .get_transaction_history(wallet, page_requested, page_size)

        return Response(status=status.HTTP_200_OK,
                        data={'success': True, 'message': 'transactions list',
                              'transactions': transaction_list,
                              'meta': meta_data})

    def post(self, request):
        """
        transaction request from one wallet to another
        post_data: from_account, to_account, amount
        """
        post_data = request.data
        from_account = post_data.get('from_account', None)
        to_account = post_data.get('to_account', None)
        amount = post_data.get('amount', None)

        # Check if all required parameters provided
        if not (from_account and to_account and amount):
            response = {
                'success': False,
                'message': 'Invalid request, parameters missing'
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

        # Check if amount requested is in valid string
        try:
            amount = float(amount)
        except ValueError:
            response = {
                'success': False,
                'message': 'Invalid requested amount'
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

        # Check if from_account provided is valid
        try:
            wallet_from = UserPHPWallet.objects.get(id=int(from_account))
        except (UserPHPWallet.DoesNotExist, ValueError) as e:
            response = {
                'success': False,
                'message': 'Invalid provided account to be debited'
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

        # Check if to_account provided is valid
        try:
            wallet_to = UserPHPWallet.objects.get(id=int(to_account))
        except (UserPHPWallet.DoesNotExist, ValueError) as e:
            response = {
                'success': False,
                'message': 'Invalid provided account to be credited'
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

        # Everything seems good, Execute transaction
        try:
            payment_done = WalletTransaction\
                .inter_wallet_payment(request.user, wallet_from,
                                      wallet_to, amount)
        except (SuspiciousRequest, InsufficientBalance, TransactionFailed), e:
            response = {
                'success': False,
                'message': e.message
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

        if payment_done:
            response = {
                'success': True,
                'message': 'Payment successful'
            }
            return Response(status=status.HTTP_200_OK, data=response)
        else:
            response = {
                'success': False,
                'message': 'Payment Unsuccessful'
            }
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=response)
