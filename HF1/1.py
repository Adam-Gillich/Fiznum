import matplotlib.pyplot as plt


def szam_osszeg(m):
    """
    This function creates a sum of a whole number's digits.
    :param m: Given whole number.
    :return: The sum m's digits.
    """

    # Make to str
    mstr = str(m)
    osszeg = 0

    # Add the digits together.
    for i in mstr:
        osszeg += int(i)  # But the integers, not strings.
    return osszeg


def szam_gyok(n):
    """
    Repeates 'szam_osszeg(m)' function, recursively, until the returned value is one digit long.
    :param n: Given whole number.
    :return: Return a one digit whole number.
    """

    k = szam_osszeg(n)

    # Checks whether k is one digit. If not call 'szam_gyok(n)' with k.
    if len(str(k)) == 1:
        return k
    else:
        return szam_gyok(k)


def oszthato(p):
    """
    Checks if the given whole 'p' is divisible by the sum of its digits.
    :param p: Given whole number.
    :return: boolean
    """

    if p == 0:
        return False
    o = p / szam_osszeg(p)
    # If the remainder of 'o' divided by 1 is 0 then 'o' is a whole number.
    if o % 1 == 0:
        return True
    else:
        return False

# --------------------------------------------


def values_of_y(N):
    """
    This function creates the values of y.
    :param N: End of range.
    :return: Values of y.
    """

    P = 0
    y = []
    for i in range(1, N):
        if oszthato(i):
            P += 1
        y.append(P / i)
    return y


def plot():
    """
    Plots the graph of 'P/N' as a function of 'N'.
    :return: The graph.
    """

    N = 1e5
    Ntoint = int(N)

    x = list(range(1, Ntoint))
    y = values_of_y(Ntoint)

    plt.plot(x, y)
    plt.title("'P/N' plotted as a function of 'N'")
    plt.xlabel('N')
    plt.ylabel('P/N')

    plt.show()

# --------------------------------------------


def num_div_by_digit_list(N):
    """
    Creates a list of numbers divisible by the sum of their digits, up to 'N'.
    :param N: Maximum range.
    :return: List of  integers.
    """

    nums = []
    for i in range(1, N):
        if oszthato(i):
            nums.append(int(i))
    return nums


def create_data(nums):
    """
    This function applies 'szam_gyok(n)' to all of 'nums' elements.
    :param nums: List of numbers.
    :return: List of numbers.
    """
    data = []
    for i in nums:
        data.append(szam_gyok(i))
    return data


def plot_hist():
    """
    Plots a histogram of numbers affected by 'szam_gyok(n)'.
    :return: The histogram.
    """

    N = 1e5
    Ntoint = int(N)

    data = create_data(num_div_by_digit_list(Ntoint))
    bins = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5]
    plt.hist(data, bins=bins, edgecolor='black', align='mid')

    plt.title("How 'szam_gyok(n)' affects numbers divisible by the sum of their digits.", fontsize=9)
    plt.xlabel('Values')
    plt.ylabel('Number of occurrences')
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9])
    plt.show()


if __name__ == "__main__":
    plot()
    # plot_hist()