def invest(amount, rate, time):
    print('principal amount: $', amount)
    print('annual rate of return:', rate)
    for n in range(1, time+1):
        amount = rate * amount + amount
        print('year', n, ': $', amount)
    print()

invest(100, .05, 8)
invest(2000, .025, 5)
