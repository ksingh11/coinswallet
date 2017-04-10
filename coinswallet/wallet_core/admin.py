# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from wallet_core.models import UserPHPWallet, PHPWalletTransaction

admin.site.register(UserPHPWallet,
                    raw_id_fields=('owner',))
admin.site.register(PHPWalletTransaction,
                    raw_id_fields=('wallet_from', 'wallet_to',))
