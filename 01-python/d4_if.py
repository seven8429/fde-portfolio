# This program takes a date input from the user in the format dd/mm/yyyy and splits it into day, month, and year components.
# 其实我想记录下写这个程序的时间，不知道什么函数，tab出来了下面这段。whatever
getdate = input("Enter the date in dd/mm/yyyy format: ")
day, month, year = getdate.split('/')
print("Day: ", day)
print("Month: ", month)
print("Year: ", year)

if day.isdigit() and month.isdigit() and year.isdigit():
    day = int(day)
    month = int(month)
    year = int(year)

    if 1 <= day <= 31 and 1 <= month <= 12 and year > 0:
        print("Valid date.today is {}/{}/{}".format(year,month,day))
    else:
        print("Invalid date")

    h=1.75
    w=80.5
    bmi=w/(h**2)
    print('BMI is:%.2f' % (bmi))
    if bmi < 18.5:
        print('过轻')
    elif 18.5 <= bmi <25:
        print('正常')
    elif 25 <= bmi <28:
        print('过重')
    elif 28 <= bmi <32:
        print('肥胖')
    else:
        print('严重肥胖')
else:
    print("Invalid input. Please enter the date in dd/mm/yyyy format.")