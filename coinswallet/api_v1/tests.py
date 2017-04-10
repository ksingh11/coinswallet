# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta
from coinswallet.settings import ACCESS_TOKEN_EXPIRE_SECONDS
from django.contrib.auth.models import User

from django.test import TestCase
from django.utils import timezone
from oauth2_provider.models import Application, AbstractApplication, \
    AccessToken
from rest_framework.test import APIClient
from wallet_core.models import UserPHPWallet


class WalletApiTestCase(TestCase):
    """
    Test cases for endpoints:
    - '/api/v1/accounts'
    - '/api/v1/payment'
    """
    def setUp(self):
        """ Seed auth users, credit wallets and generate authenticate user """
        # Create test users
        test_users = ['bob123', 'alice456']
        self.username_list = test_users + ['Mabel', 'Laure', 'Erich', 'Tara',
                                           'Alethia', 'Brendan', 'Yoshie',
                                           'Bethanie', 'Faviola', 'Ignacia',
                                           'Ilse', 'Fletcher', 'Newton',
                                           'Cathy', 'Isis', 'Sherlene',
                                           'Vida', 'Grady']
        for name in self.username_list:
            User.objects.create(username=name.lower(), first_name=name)

        # auth users for testing
        self.user_bob = User.objects.filter(username=test_users[0]).first()
        self.user_alice = User.objects.filter(username=test_users[1]).first()

        # credit 500 to every wallet
        self.initial_balance = 500
        UserPHPWallet.objects.all().update(balance=self.initial_balance)

        # configure oauth app, and get access token, scopes: view transact
        self.app = Application(
            name='TestApp',
            authorization_grant_type=AbstractApplication.GRANT_PASSWORD,
            client_type=AbstractApplication.CLIENT_CONFIDENTIAL
        )
        self.app.save()

        # Authenticate user bob, will be using this user in further test
        access_token_bob = AccessToken.objects\
            .create(user=self.user_bob,
                    scope='view transact',
                    expires=timezone.now()
                    + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS),
                    token='some-really-secret-access_token',
                    application=self.app)
        # set API client for api calls
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '
                                                   + access_token_bob.token)

    def test_accounts_get_api(self):
        """
        API: GET /api/v1/accounts/
        Lists, all accounts with pagination
        """
        # response meta data contains total accounts
        response = self.client.get('/api/v1/accounts/?page=1')
        self.assertEqual(response.data['meta']['total_count'], 20,
                         'Broken: Accounts response incorrect')

        # number of accounts in list is equal to per_page query string
        response = self.client.get('/api/v1/accounts/?page=1&per_page=13')
        self.assertEqual(len(response.data['accounts']), 13,
                         'Account list, pagination not working properly')

        # account list are in ordered by 'id' ascending
        response = self.client.get('/api/v1/accounts/?page=1&per_page=25')
        self.assertEqual(response.data['accounts'][1]['owner'], 'alice456',
                         'Account list, order incorrect')

    def test_payments_post_api(self):
        """API: POST /api/v1/payments/ to transfer amount to other wallet"""
        alice_wallet = self.user_alice.user_wallet
        bob_wallet = self.user_bob.user_wallet

        # sending wallet not owned by logged in user, responds status code 400
        response = self.client.post('/api/v1/payments/',
                                    {'from_account': alice_wallet.id,
                                     'to_account': bob_wallet.id,
                                     'amount': 10}, format='json')
        self.assertEqual(response.status_code, 400,
                         'Broken: invalid status code')

        # transferring amount to self account, not permitted
        response = self.client.post('/api/v1/payments/',
                                    {'from_account': bob_wallet.id,
                                     'to_account': bob_wallet.id,
                                     'amount': 10}, format='json')
        self.assertEqual(response.status_code, 400,
                         'Broken: invalid status code')
        self.assertEqual(response.data['success'], False,
                         'Broken: allowing payment transfer to same account')

        # transferring amount more than account balance not permitted
        response = self.client.post('/api/v1/payments/',
                                    {'from_account': bob_wallet.id,
                                     'to_account': alice_wallet.id,
                                     'amount': 1000}, format='json')
        self.assertEqual(response.status_code, 400,
                         'Broken: invalid status code')
        self.assertEqual(response.data['success'], False,
                         'Broken: allowing transfer amount than balance')

        # transfer working, if everything is good,
        # transfer amount from authenticated user (bob) to account (alice)
        transfer_amount = 50
        response = self.client.post('/api/v1/payments/',
                                    {'from_account': bob_wallet.id,
                                     'to_account': alice_wallet.id,
                                     'amount': transfer_amount}, format='json')
        self.assertEqual(response.status_code, 200,
                         'Broken: invalid status code')
        self.assertEqual(response.data['success'], True,
                         'Broken: amount transfer not working')

        # amount is credited to recipient's account
        response = self.client.get('/api/v1/accounts/?page=1&per_page=25')
        self.assertEqual(response.data['accounts'][1]['balance'],
                         self.initial_balance + transfer_amount,
                         'Payment transfer, amount not crediting')

        # amount is being debited from sender's account
        response = self.client.get('/api/v1/accounts/?page=1&per_page=25')
        self.assertEqual(response.data['accounts'][0]['balance'],
                         self.initial_balance - transfer_amount,
                         'Payment transfer, amount not debiting')

        # transfer to same wallet and amount twice is not allowed,
        # to prevent any suspicious transfer
        transfer_amount = 50
        response = self.client.post('/api/v1/payments/',
                                    {'from_account': bob_wallet.id,
                                     'to_account': alice_wallet.id,
                                     'amount': transfer_amount}, format='json')
        self.assertEqual(response.status_code, 400,
                         'Broken: invalid status code')
        self.assertEqual(response.data['success'], False,
                         'Broken: allowing transfer to same account')

    def test_payment_get_api(self):
        """
        API: GET /api/v1/payments/
        List all transaction of user logged in
        """
        alice_wallet = self.user_alice.user_wallet
        bob_wallet = self.user_bob.user_wallet

        # Make 5 transaction for further test cases
        for i in range(1, 6):
            transfer_amount = i * 10
            response = self.client.post('/api/v1/payments/',
                                        {'from_account': bob_wallet.id,
                                         'to_account': alice_wallet.id,
                                         'amount': transfer_amount},
                                        format='json')

        # api is working and if all transactions listing
        response = self.client.get('/api/v1/payments/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200,
                         'Broken: invalid status code')
        self.assertEqual(response.data['success'], True,
                         'Get api not working')
        self.assertEqual(len(response.data['transactions']), 5,
                         'Get transaction, not listing all')

        # pagination is working, responds according to per_page query string
        response = self.client.get('/api/v1/payments/?page=1&per_page=3')
        self.assertEqual(len(response.data['transactions']), 3,
                         'Get transaction, pagination broken')
