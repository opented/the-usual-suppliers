import babel.numbers
import babel.dates
import decimal

from flask import request

from tus.core import app


def group(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))


@app.template_filter('currency')
def format_eur(num):
    if num is None or (isinstance(num, basestring) and not len(num)):
        return '-'
    try:
        num = int(decimal.Decimal(num))
        num = babel.numbers.format_currency(num, "EUR", locale="en_US")
        return num.replace('.00', '')
    except Exception, e:
        return '-'


@app.template_filter('format_num')
def format_num(num):
    if num is None or (isinstance(num, basestring) and not len(num)):
        return '-'
    try:
        return group(int(num))
    except Exception, e:
        raise
        return '-'


def arg_default(name, default):
    val = request.args.get(name)
    if val is None:
        return default
    val = val.strip()
    if not len(val):
        return default
    return val
