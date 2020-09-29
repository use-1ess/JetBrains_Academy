from math import log, ceil, floor
import argparse
import sys


def throw_error_and_exit():
    error_message = 'Incorrect parameters'
    print(error_message)
    sys.exit(1)


# parse and check user defined parameters
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        type=str
    )
    parser.add_argument(
        "--payment",
        type=float
    )
    parser.add_argument(
        "--principal",
        type=float
    )
    parser.add_argument(
        "--periods",
        type=int
    )
    parser.add_argument(
        "--interest",
        type=float
    )
    args = parser.parse_args()
    # arguments checks
    if args.type not in ['annuity', 'diff']:
        throw_error_and_exit()
    if args.payment and args.type == 'diff':
        throw_error_and_exit()
    if not args.interest:
        throw_error_and_exit()
    if len([arg for arg in vars(args).values() if arg]) < 4:
        throw_error_and_exit()
    return args


# function to calculate floating point period interest rate from annual percent interest rate
def calc_period_ir(annual_ir):
    return (annual_ir / 12) / 100


# function to create plural form
def make_plural(number, noun):
    if number == 1:
        return f"{number} {noun}"
    else:
        return f"{number} {noun}s"


def calc_overpayment(initial_principal, period, period_payment):
    return ceil(float(period_payment) * float(period) - float(initial_principal))


def calc_months_to_pay(user_defined_vals):
    period_interest_rate = calc_period_ir(user_defined_vals.interest)
    number_of_periods = log(
        (
                user_defined_vals.payment
                / (
                        user_defined_vals.payment
                        - (period_interest_rate * user_defined_vals.principal)
                )
        ),
        1 + period_interest_rate
    )
    result_periods = ceil(number_of_periods)
    return {
        "periods": result_periods,
        "years": result_periods // 12,
        "months": result_periods % 12
    }


def calc_annuity_pay(user_defined_vals):
    period_interest_rate = calc_period_ir(user_defined_vals.interest)
    annuity_pay = (
            user_defined_vals.principal
            * (
                    (
                            period_interest_rate
                            * ((1 + period_interest_rate) ** user_defined_vals.periods)
                    )
                    / (
                            ((1 + period_interest_rate) ** user_defined_vals.periods) - 1
                    )
            )
    )
    return annuity_pay


def calc_load_principal(user_defined_vals):
    period_interest_rate = calc_period_ir(user_defined_vals.interest)
    loan_principal = (
            user_defined_vals.payment
            / (
                    (
                            period_interest_rate
                            * ((1 + period_interest_rate) ** user_defined_vals.periods)
                    )
                    / (
                            ((1 + period_interest_rate) ** user_defined_vals.periods) - 1
                    )
            )
    )
    return floor(loan_principal)


def calc_diff_payments(user_defined_vals):
    def define_main_formula(principal, interest_rate, num_month, curr_month):
        result = (
                principal / num_month
                + interest_rate
                * (
                    principal
                    - (
                        (
                            principal
                            * (curr_month - 1)
                        )
                        / num_month
                    )
                )
        )
        return result
    period_interest_rate = calc_period_ir(user_defined_vals.interest)
    payments_schedule = {}
    current_month = 1
    total_months = user_defined_vals.periods
    for _ in range(total_months):
        curr_payment = define_main_formula(
                            user_defined_vals.principal,
                            period_interest_rate,
                            total_months,
                            current_month
                        )
        payments_schedule[current_month] = (ceil(curr_payment))
        current_month += 1
    return payments_schedule


user_defined_values = get_args()
if user_defined_values.type == 'annuity':
    if not user_defined_values.periods:
        periods = calc_months_to_pay(user_defined_values)
        if periods['years'] == 0:
            print(f"It will take {make_plural(periods['months'], 'month')} to repay this loan!")
        elif periods['months'] == 0:
            print(f"It will take {make_plural(periods['years'], 'year')} to repay this loan!")
        else:
            print(
                f"It will take {make_plural(periods['years'], 'year')} and {make_plural(periods['months'], 'month')} to repay this loan!")
        print(
            f"Overpayment = {calc_overpayment(user_defined_values.principal, user_defined_values.payment, periods['periods'])}")
    elif not user_defined_values.payment:
        annuity_payment = ceil(calc_annuity_pay(user_defined_values))
        print(f"Your monthly payment = {annuity_payment}!")
        print(
            f"Overpayment = {calc_overpayment(user_defined_values.principal, annuity_payment, user_defined_values.periods)}")
    elif not user_defined_values.principal:
        total_lp = calc_load_principal(user_defined_values)
        print(f"Your loan principal = {total_lp}!")
        print(f"Overpayment = {calc_overpayment(total_lp, user_defined_values.payment, user_defined_values.periods)}")
else:
    diff_loan_result = calc_diff_payments(user_defined_values)
    total_diff_loan_cost = sum(diff_loan_result.values())
    for month_pay in diff_loan_result:
        print(f"Month {month_pay}: payment is {diff_loan_result[month_pay]}")
    print(f"Overpayment = {ceil(total_diff_loan_cost - user_defined_values.principal)}")
