def hdiv(dividend, divisor, precision=0):
    """高精度计算除法，没有四舍五入

    @author: cidplp

    @param dividend:被除数
    @type dividend:int
    @param divisor:除数
    @type divisor:int
    @param precision:小数点后精度
    @type precision:int
    @return:除法结果
    @rtype:str
    """

    if isinstance(precision, int) == False or precision < 0:
        print('精度必须为非负整数')
        return

    a = dividend
    b = divisor

    # 有负数的话做个标记
    if abs(a + b) == abs(a) + abs(b):
        flag = 1
    else:
        flag = -1

        # 变为正数，防止取模的时候有影响
    a = abs(a)
    b = abs(b)

    quotient = a // b
    remainder = a % b

    if remainder == 0:
        return quotient

    ans = str(quotient) + '.'

    i = 0
    while i < precision:
        a = remainder * 10
        quotient = a // b
        remainder = a % b
        ans += str(quotient)
        if remainder == 0:
            break
        i += 1

    if precision == 0:
        ans = ans.replace('.', '')

    if flag == -1:
        ans = '-' + ans

    return ans