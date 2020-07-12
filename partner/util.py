# -*- mode: python; coding: utf-8; -*-
from math import exp

import ledger


def discount(amount, rate, time, ndigits=2):
    """Return the amount discounted by continuous rate and time."""
    c, v = amount.commodity, amount.to_double()
    vt = round(v * exp(-rate * time), ndigits)
    return ledger.Amount(c.symbol + str(vt))


def depreciate(amount, rate, t0, T, ndigits=2):
    """Return the depreciation between two points in time.

    This function returns positive values for depreciation and
    negative values for appreciation.

    """
    c, v = amount.commodity, amount.to_double()
    vt = round(v * (exp(-rate * t0) - exp(-rate * T)), ndigits)
    return ledger.Amount(c.symbol + str(vt))

