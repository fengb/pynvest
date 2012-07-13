import datetime
import decimal
import re


_DATE_LIKE = re.compile('^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}$')
_NUMBER_LIKE = re.compile('^[0-9.]+$')
def convert_string(field):
    if _DATE_LIKE.match(field):
        return datetime.date(*map(int, field.split('-')))
    elif _NUMBER_LIKE.match(field):
        return decimal.Decimal(field)
    else:
        return field


if __name__ == "__main__":
    import doctest
    doctest.testmod()
