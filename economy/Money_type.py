from enum import Enum


class MoneyType(Enum):
    RS3 = 1
    R07 = 2
    TOKENS = 3
    WagRS3 = 4
    WagR07 = 5

    def format_string(self):
        if self == MoneyType.R07:
            return "07"
        else:
            return self.name

    def min_amount(self):
        if self == MoneyType.RS3:
            return 1000000
        else:
            return 100000
