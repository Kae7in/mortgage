import math


class Mortgage:
    def __init__(self, principal=0, apr=0.0, periods=0):
        # foundation of the loan
        self.principal = principal
        self.apr = apr / 100.0
        self.r = apr / 100.0 / 12.0
        self.periods = periods

        self.normal_cache = {}
        self.extra_cache = {}

    def pi_payment(self, extra=0):
        if self.principal <= 0 or self.apr <= 0 or self.periods <= 0:
            raise ValueError("Mortgage info incomplete or incorrect. Cannot calculate monthly payment (PI).")

        numerator = self.r * self.principal
        denominator = 1.0 - math.pow(1.0+self.r, -self.periods)
        payment = numerator / denominator

        return payment + extra

    def make_payment(self, extra=0):
        pass

    def pi_breakdown(self, period):
        pi_tuple = (self.pi_payment() - self.interest(period), self.interest(period))
        return pi_tuple

    def balance(self, period, extra=0, freq=12):
        if extra == 0 or freq == 12:
            left_term = math.pow(1 + self.r, period) * self.principal
            right_term = ((math.pow(1 + self.r, period) - 1) * (self.pi_payment()+extra)) / self.r
            return left_term - right_term
        elif extra > 0 and freq != 12:
            p = self.principal
            f = freq
            for i in range(1, period+1):
                p = ((1 + self.r)*p) - self.pi_payment()
                if f > 0:
                    p -= extra
                    f -= 1
                if i % 12 == 0:
                    f = freq
            return p

    def interest(self, period, extra=0):
        interest = 0
        previous_interest_total = 0
        i = 0

        if extra == 0:
            if period in self.normal_cache:
                return self.normal_cache[period]
        elif extra != 0:
            if period in self.extra_cache:
                return self.extra_cache[period]

        for i in range(1, period):
            previous_interest_total = (i*self.pi_payment(extra=extra)) + self.balance(i, extra=extra) - self.principal
        interest = (period*self.pi_payment(extra=extra)) + self.balance(period, extra=extra) - self.principal - previous_interest_total
        interest = interest if interest >= 0 else 0

        if extra == 0:
            self.normal_cache[period] = interest
        elif extra != 0:
            self.extra_cache[period] = interest

        return interest

    def interest_for_range(self, begin_period, end_period, extra=0):
        total_interest = 0
        for period in range(begin_period, end_period):
            total_interest += self.interest(period, extra=extra)
        return total_interest

    def total_interest(self):
        total = (self.pi_payment() * self.periods) - self.principal
        return total

    def __str__(self):
        readable_string = 'Principal: ${}'.format(self.principal) + '\n'\
                            + 'Rate: ' + str(self.apr * 100.0) + '%\n'\
                            + 'Term: ' + str(self.periods) + ' months\n'\
                            + 'Monthly Payment (PI): {:06.2f}'.format(self.pi_payment())
        return readable_string
        

if __name__ == "__main__":
    m = Mortgage(200000, 3.6 , 360)

    per_month = 100
    diff_total = 0
    saved = 0
    for i in range(1, 31):  # Years
        for j in range(1, 13):  # Months
            period = (i-1)*12 + j
            cumulative_interest_1 = m.interest_for_range(1, period+1)
            cumulative_interest_2 = m.interest_for_range(1, period+1, extra=per_month)
            saved = cumulative_interest_1 - cumulative_interest_2

            interest_1 = m.interest(period)
            interest_2 = m.interest(period, extra=per_month)
            print('{}  normal=${:04.2f}'.format(period, interest_1) + ', with extra=${:04.2f}'.format(interest_2) + ' --- ' + 'diff=${:04.2f}'.format(interest_1-interest_2) + ' --- ' + 'total saved=${:04.2f}'.format(saved))
            
            diff_total += (interest_1 - interest_2)
        print('END OF YEAR ' + str(i) + ' --- ${:04.2f} saved this year --- ${:04.2f}'.format(diff_total, saved) + ' total saved')
        print('-------------------------------------------------------------------------')
        diff_total = 0