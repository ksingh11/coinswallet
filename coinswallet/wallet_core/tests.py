# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.test import TestCase
from wallet_core.exceptions import InsufficientBalance, SuspiciousRequest
from wallet_core.models import UserPHPWallet
from wallet_core.views import WalletTransaction


class WalletTestCase(TestCase):
    def setUp(self):
        """Create test users, allot 500 to wallet of each"""

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

    def test_all_wallet_created_and_credited(self):
        """a wallets are getting created for every user creation"""
        total_wallets = UserPHPWallet.objects.count()
        self.assertEqual(len(self.username_list), total_wallets,
                         'All wallets not getting created')

        wallets_credited = UserPHPWallet.objects\
                                        .filter(balance=self.initial_balance)\
                                        .count()
        self.assertEqual(len(self.username_list), wallets_credited,
                         'All wallets not credited with initial balance')

    def test_inter_wallet_payment(self):
        """
        Test wallet to wallet transaction, and the exceptions getting raised
        """
        user_bob_wallet = UserPHPWallet.objects.get(owner=self.user_bob)
        user_alice_wallet = UserPHPWallet.objects.get(owner=self.user_alice)
        request_user = self.user_bob

        # transfer amount from user_bob to user_alice
        # InsufficientBalance exception raised on low balance
        self.assertRaisesMessage(InsufficientBalance,
                                 'Insufficient Balance',
                                 WalletTransaction.inter_wallet_payment,
                                 request_user, user_bob_wallet,
                                 user_alice_wallet, amount=501)

        # transfer between same wallets not allowed
        self.assertRaisesMessage(SuspiciousRequest,
                                 'Cannot transfer payment to own wallet',
                                 WalletTransaction.inter_wallet_payment,
                                 request_user, user_bob_wallet,
                                 user_bob_wallet, amount=10)

        # logged in user is able to send payment from his wallet only.
        self.assertRaisesMessage(SuspiciousRequest,
                                 'Unauthorised Access',
                                 WalletTransaction.inter_wallet_payment,
                                 request_user, user_alice_wallet,
                                 user_bob_wallet, amount=10)

        # transaction successful
        bob_initial_amount = user_bob_wallet.balance
        alice_initial_amount = user_alice_wallet.balance
        amount = 25
        result = WalletTransaction.inter_wallet_payment(request_user,
                                                        user_bob_wallet,
                                                        user_alice_wallet,
                                                        amount)
        self.assertTrue(result)

        # final standing of both wallets updated
        user_bob_wallet.refresh_from_db()
        user_alice_wallet.refresh_from_db()
        self.assertEqual(bob_initial_amount - amount,
                         user_bob_wallet.balance)
        self.assertEqual(alice_initial_amount + amount,
                         user_alice_wallet.balance)
