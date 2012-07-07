import datetime
import decimal


def convert_string(field):
    if '-' in field:
        return datetime.date(*map(int, field.split('-')))
    else:
        return decimal.Decimal(field)
