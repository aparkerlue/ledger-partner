# -*- mode: python; coding: utf-8; -*-
"""Functions for partnership accounting with Ledger."""
from math import floor

from ledger import Amount


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    """Return True if the values a and b are close to each other."""
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def parse_partner_string(s):
    """Return a dict of partner labels to percentages summing to one."""
    L = [x.strip().split(" ") for x in s.split(",")]

    # Numberless spec indicates equal weighting.
    if all(len(x) <= 1 for x in L):
        return {t[0]: 100 / len(L) for t in L}

    # There should be no more than a single elided amount.
    n_elisions = len([None for t in L if len(t) <= 1])
    if n_elisions == 0:
        spec = {t[0]: float(t[1]) for t in L}
        n = sum(spec.values())
        if n != 100:
            raise ValueError("spec values do not total 100: %s" % n)
    elif n_elisions == 1:
        spec = {
            t[0]: float(t[1])
            if len(t) > 1
            else 100 - sum(float(u[1]) for u in L if len(u) > 1)
            for t in L
        }
    else:
        assert n_elisions > 1
        raise ValueError("number of elided values exceeds 1: %s" % n_elisions)

    assert sum(spec.values()) == 100
    return spec


def attribute_to_partner_strict(partner, partner_string_or_spec, amount):
    """Return the amount attributable to the given partner."""
    spec = (
        partner_string_or_spec
        if isinstance(partner_string_or_spec, dict)
        else parse_partner_string(partner_string_or_spec)
    )
    if partner not in spec:
        raise ValueError("Partner not found in partner string: %s" % partner)
    v100 = spec[partner] * float(amount.abs())
    f_floor = round if isclose(v100, round(v100)) else floor
    v = amount.sign() * 0.01 * f_floor(v100)
    return Amount(str(v)).with_commodity(amount.commodity)


def attribute_to_partner(partner, partner_string_or_spec, amount):
    """Return the amount attributable to the given partner."""
    try:
        a = attribute_to_partner_strict(partner, partner_string_or_spec, amount)
    except ValueError:
        a = Amount(0)
    return a


def attribute_to_residual(partner_string, amount, digits_of_precision=2):
    """Return the residual amount not attributable to any partners."""
    spec = parse_partner_string(partner_string)
    v = round(
        float(amount)
        - sum(float(attribute_to_partner(partner, spec, amount)) for partner in spec),
        digits_of_precision,
    )
    return Amount(str(v)).with_commodity(amount.commodity)


def signed_unit_amount(amount):
    """Return amount with its sign and unit magnitude."""
    return amount / amount.abs()


def partner_in_partner_string(partner, partner_string):
    """Return true if partner is present in partner string."""
    return partner in parse_partner_string(partner_string)
