from . import models, util
import operator


class LotSummary(object):
    def __init__(self, lots):
        if len(lots) < 1:
            raise ValueError
        if len(set(l.investment for l in lots)) > 1:
            raise ValueError

        self.lots = lots

    def investment(self):
        return self.lots[0].investment

    def outstanding_shares(self):
        return sum(l.outstanding_shares for l in self.lots)

    @classmethod
    def group_by_investment(cls, lots):
        return [cls(ls) for (investment, ls) in util.groupbyrollup(lots, key=operator.attrgetter('investment'))]
