"""FizzBuzz: Print numbers 1-100, replacing multiples of 3 with 'Fizz',
multiples of 5 with 'Buzz', and multiples of both with 'FizzBuzz'.
"""


def fizzbuzz(n):
    """Return the FizzBuzz string for a given number."""
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    return str(n)


if __name__ == "__main__":
    for i in range(1, 101):
        print(fizzbuzz(i))
