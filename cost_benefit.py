import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

import pdb

pd.options.mode.chained_assignment = None

# GENERAL
discount = 0.05
utilities = 250.00
food = 500.00
personal = 570.00
luxury = 860.00
rent_now = 675.00
avg_rent = 1000.00
leave_apt = 7 #months
leave_LR = 60 #months
Sam = 2900.00 #income
Kikumi = 3060.00 #income
wage_inflation = 0.02/12


# HOUSE
interest = 0.045/12
mortgage_life = 180 #months
first_house = 120000.00
sell_first = 240 #months
second_house = 250000.00
PMI = 75.00
tax = (0.014/12)
percent_down = 0.05
closing = 0.04
insurance = 75.00
appreciation = 0.04/12


# RENTAL
mgmt = 0.1
maintenance = first_house*0.015/12
contingency = 0.05
occupancy = 0.85
rental_tax = first_house*tax


def mortgage_payment(house,down,i,n):
    p = house-(house*down)
    return p*(i*(1+i)**n)/((1+i)**n-1)
    # return P/((1+i)**n/(i*(1+i)**n))

def present_value(future,r,n):
    return future/(1+r)**n

def salvage_value(principle,life,months_paid,monthly_payment):
    #assume all payments interest-only until total interest paid.
    total_cost = monthly_payment*life
    total_interest = total_cost - principle
    paid_in = monthly_payment*months_paid
    equity = paid_in - total_interest
    return equity

def rental_income(rent,fees,maint,cont,occupancy,rental_tax):
    return rent*occupancy-(rent*(fees+cont))-maint-rental_tax


dates = pd.date_range(start='20180701',end='20550701',freq='MS')

# No Action Alternative
noact = pd.DataFrame(index=dates)
noact['month number'] = pd.Series([i for i in range(len(noact))],index=dates)
noact['fixed costs'] = -utilities-food-personal-luxury
noact['housing costs'] = -rent_now
noact['income'] = (Sam+Kikumi)*(1+wage_inflation)**noact['month number']
noact['cash flow'] = noact['fixed costs']+noact['housing costs']+noact['income']
noact['cumulative cash flow'] = noact['cash flow'].cumsum()
noact['present value'] = present_value(noact['cash flow'],discount,noact['month number'])

# print('\n')
print('NPV of no action alternative: {}'.format(noact['present value'].sum()))
print('Cumulative cash flow: {}'.format(noact['cumulative cash flow'][-1]))

# Rent and buy in 5

wait5 = pd.DataFrame(index=dates)
wait5['month number'] = pd.Series([i for i in range(len(wait5))],index=dates)
wait5['fixed costs'] = -utilities-food-personal-luxury
# Housing costs after 5 years
wait5['housing costs'] = pd.Series(0,index=dates) # empty series
house_payment = mortgage_payment(second_house,percent_down,interest,mortgage_life)
house_payment = house_payment+PMI+insurance
initial_payment = second_house*(percent_down+closing)
mortgage_end = leave_LR+mortgage_life
wait5['housing costs'].iloc[0:leave_apt] += -rent_now
wait5['housing costs'].iloc[leave_apt:leave_LR] += -avg_rent
wait5['housing costs'].iloc[leave_LR:] += -house_payment
wait5['housing costs'].iloc[leave_LR] += -initial_payment
# wait5['housing costs'] = pd.concat([lease,new_lease,mortgage])
wait5['income'] = (Sam+Kikumi)*(1+wage_inflation)**wait5['month number']
wait5['income'].iloc[-1] += second_house*(1+appreciation)**wait5['month number'].iloc[-1] # remaining home equity
wait5['cash flow'] = wait5['fixed costs']+wait5['housing costs']+wait5['income']
wait5['cumulative cash flow'] = wait5['cash flow'].cumsum()
wait5['present value'] = present_value(wait5['cash flow'],discount,wait5['month number'])

# print('\n')
print('NPV of waiting 5 years alternative: \t\t{}'.format(wait5['present value'].sum()))
print('Cumulative cash flow: {}'.format(wait5['cumulative cash flow'][-1]))
print('Total house payment {}'.format(house_payment))

# Buy at lease end, upgrade in 5 and rent

rentout = pd.DataFrame(index=dates)
rentout['month number'] = pd.Series([i for i in range(len(rentout))],index=dates)
rentout['fixed costs'] = -utilities-food-personal-luxury
rentout['housing costs'] = pd.Series(0,index=dates) # empty Series
rentout['housing costs'].iloc[0:leave_apt] += -rent_now
# First home
first_house_payment = mortgage_payment(first_house,percent_down,interest,mortgage_life)
first_house_payment = first_house_payment+PMI+insurance
first_initial_payment = first_house*(percent_down+closing)
first_mortgage_end = leave_apt+mortgage_life
rentout['housing costs'].iloc[leave_apt:first_mortgage_end] += -first_house_payment
rentout['housing costs'].iloc[leave_apt] += -first_initial_payment
# Second home
second_house_payment = mortgage_payment(second_house,percent_down,interest,mortgage_life)
second_house_payment = second_house_payment+PMI+insurance
second_initial_payment = second_house*(percent_down+closing)
second_mortgage_end = leave_LR+mortgage_life
rentout['housing costs'].iloc[leave_LR:second_mortgage_end] += -second_house_payment
rentout['housing costs'].iloc[leave_LR] += -second_initial_payment
# Income
rentout['income'] = (Sam+Kikumi)*(1+wage_inflation)**rentout['month number']
net_rent = rental_income(avg_rent,mgmt,maintenance,contingency,occupancy,rental_tax)
rentout['income'].iloc[leave_LR:] += net_rent
rentout['income'].iloc[-1] += (second_house + first_house)*(1+appreciation)**rentout['month number'].iloc[-1]
rentout['cash flow'] = rentout['fixed costs']+rentout['housing costs']+rentout['income']
rentout['cumulative cash flow'] = rentout['cash flow'].cumsum()
rentout['present value'] = present_value(rentout['cash flow'],discount,rentout['month number'])

# print('\n')
print('NPV of buy and upgrade alternative: {}'.format(rentout['present value'].sum()))
print('Cumulative cash flow: {}'.format(noact['cumulative cash flow'][-1]))
print('House payment: {0} and {1}'.format(first_house_payment,second_house_payment))

# Buy, upgrade, rent, sell in 20

sell = pd.DataFrame(index=dates)
sell['month number'] = pd.Series([i for i in range(len(sell))],index=dates)
sell['fixed costs'] = -utilities-food-personal-luxury
sell['housing costs'] = pd.Series(0,index=dates) # empty Series
sell['housing costs'].iloc[0:leave_apt] = -rent_now
# First home
first_house_payment = mortgage_payment(first_house,percent_down,interest,mortgage_life)
fhp = first_house_payment # convenience variable for salvage_value calculation
first_house_payment = first_house_payment+PMI+insurance
first_initial_payment = first_house*(percent_down+closing)
first_mortgage_end = sell_first
sell['housing costs'].iloc[leave_apt:first_mortgage_end] += -first_house_payment
sell['housing costs'].iloc[leave_apt] += -first_initial_payment
# Second home
second_house_payment = mortgage_payment(second_house,percent_down,interest,mortgage_life)
second_house_payment = second_house_payment+PMI+insurance
second_initial_payment = second_house*(percent_down+closing)
second_mortgage_end = leave_LR+mortgage_life
sell['housing costs'].iloc[leave_LR:second_mortgage_end] += -second_house_payment
sell['housing costs'].iloc[leave_LR] += -second_initial_payment
# Income
sell['income'] = (Sam+Kikumi)*(1+wage_inflation)**sell['month number']
net_rent = rental_income(avg_rent,mgmt,maintenance,contingency,occupancy,rental_tax)
months_paid = sell_first - leave_apt
salvage = salvage_value(first_house,mortgage_life,months_paid,fhp)
sell['income'].iloc[sell_first] += salvage*(1+appreciation)**sell['month number'].iloc[sell_first]
sell['income'].iloc[leave_LR:sell_first] += net_rent
sell['income'].iloc[-1] += second_house*(1+appreciation)**sell['month number'].iloc[-1]
sell['cash flow'] = sell['fixed costs']+sell['housing costs']+sell['income']
sell['cumulative cash flow'] = sell['cash flow'].cumsum()
sell['present value'] = present_value(sell['cash flow'],discount,sell['month number'])

# print('\n')
print('NPV of buy, upgrade and sell alternative: {}'.format(sell['present value'].sum()))
print('Cumulative cash flow: {}'.format(noact['cumulative cash flow'][-1]))
print('House payments: {0} and {1}'.format(first_house_payment,second_house_payment))


# Plot it all out
# noact.plot(kind='line',y=['cash flow','cumulative cash flow'])
# plt.savefig('noact.png')
# wait5.plot(kind='line',y=['cash flow','cumulative cash flow'])
# plt.savefig('wait5.png')
# rentout.plot(kind='line',y=['cash flow','cumulative cash flow'])
# plt.savefig('rentout.png')
# sell.plot(kind='line',y=['cash flow','cumulative cash flow'])
# plt.savefig('sell.png')
