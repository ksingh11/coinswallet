# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.global_settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils.translation import ugettext_lazy as _

from django.db import models


class UserPHPWallet(models.Model):
    """
    User's wallet: Amount stored are in PHP currency.
    Note:
    - Designed so that one user can not have more than PHP Wallet.
    - If any other currency, first need to convert it to PHP currency
    """
    owner = models.OneToOneField(to=AUTH_USER_MODEL,
                                 on_delete=models.PROTECT,
                                 related_name='user_wallet',
                                 verbose_name=_('Wallet Owner'))

    balance = models.FloatField(verbose_name=_('Account Balance'),
                                default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.owner.get_username()


@receiver(post_save, sender=AUTH_USER_MODEL)
def create_user_wallet(**kwargs):
    """ Create the the PHP Wallet for every new user getting created """
    if kwargs['created']:
        UserPHPWallet.objects.get_or_create(owner=kwargs['instance'])


class PHPWalletTransaction(models.Model):
    """ Records transactions made from one PHP wallet to other PHP wallet """
    wallet_from = models.ForeignKey(to=UserPHPWallet,
                                    on_delete=models.PROTECT,
                                    related_name='wallet_from',
                                    verbose_name=_('From wallet'))

    wallet_to = models.ForeignKey(to=UserPHPWallet,
                                  on_delete=models.PROTECT,
                                  related_name='wallet_to',
                                  verbose_name=_('To Wallet'))

    amount = models.FloatField(blank=False, null=False,
                               verbose_name=_('transaction amount'))

    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(PHPWalletTransaction, self).save(*args, **kwargs)

        # check if wallet_from, wallet_to are same
        if self.wallet_from == self.wallet_to:
            raise ValidationError('Cannot transfer payment to own wallet')

    def __unicode__(self):
        """ String representation of the transaction entry """
        return "From: %s -> To: %s, Amount: %s" % \
               (self.wallet_from.owner.get_username(),
                self.wallet_to.owner.get_username(),
                str(self.amount))

    class Meta:
        ordering = ('-created',)
