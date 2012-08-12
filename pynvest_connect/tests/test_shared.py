import datetime
import decimal

import pynvest_connect.shared


class TestConvertString(object):
    def test_number(self):
        assert pynvest_connect.shared.convert_string('123.45') == decimal.Decimal('123.45')

    def test_date(self):
        assert pynvest_connect.shared.convert_string('1984-02-04') == datetime.date(1984, 2, 4)

    def test_string(self):
        assert pynvest_connect.shared.convert_string('never gonna give you up') == 'never gonna give you up'
