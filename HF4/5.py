import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import sympy as sp
from IPython.display import display, Math


def SetTex():
    """
    Sets TeX fonts.
    """

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


def my_Taylor(func, x, n, x0=0):
    result = func.subs(x, x0)
    for i in range(1, n):
        result += sp.diff(func, x, i).subs(x, x0) * (x-x0)**i / sp.factorial(i)

    return result


def pade_approximation_function(series, m, n):
    # Asset flip form https://approximaths.com/2025/09/25/python-code-for-pade-approximants/
    """
    Returns the Padé approximation [m/n] in the form of a rational function
    with coefficients simplified as fractions.

    Parameters:
    series : list - Coefficients of the Taylor series (e.g., [1, 0, -1/2, 0, 1/24, ...] for cos(x))
    m : int - Degree of the numerator
    n : int - Degree of the denominator

    Returns:
    sympy.Expr - Rational function P(x)/Q(x) with simplified fractions
    """
    # Check that there are enough terms in the series
    if len(series) < m + n + 1:
        raise ValueError(f"The series must contain at least {m + n + 1} terms for an [m/n] approximation")

    # Convert the series coefficients to simplified fractions
    series = [sp.simplify(sp.Rational(str(c))) for c in series]

    # Symbolic variable
    x = sp.Symbol('x')

    # Coefficients of the numerator P(x) = a0 + a1*x + ... + am*x^m
    a = [sp.Symbol(f'a{i}') for i in range(m + 1)]
    # Coefficients of the denominator Q(x) = 1 + b1*x + ... + bn*x^n (b0 = 1)
    b = [1] + [sp.Symbol(f'b{i}') for i in range(1, n + 1)]

    # Polynomials P(x) and Q(x)
    P = sum(ai * x ** i for i, ai in enumerate(a))
    Q = sum(bi * x ** i for i, bi in enumerate(b))

    # The truncated series in polynomial form
    S = sum(c * x ** i for i, c in enumerate(series))

    # Equation to solve: P(x) - Q(x)*S(x) = 0 up to order m+n
    expr = P - Q * S

    # Extract coefficients of x^0 to x^(m+n) and set the equations to 0
    equations = [sp.expand(expr).coeff(x, k) for k in range(m + n + 1)]

    # Variables to solve for (a0, a1, ..., am, b1, b2, ..., bn)
    unknowns = a + b[1:]

    # Solve the system
    solution = sp.solve(equations, unknowns)

    if not solution:
        raise ValueError("No solution found for this approximation")

    # Simplified coefficients for P(x) and Q(x)
    num_coeffs = [sp.simplify(sp.Rational(str(solution[ai]))) if ai in solution else 0 for ai in a]
    den_coeffs = [1] + [sp.simplify(sp.Rational(str(solution[bi]))) if bi in solution else 0 for bi in b[1:]]

    # Construct the final polynomials
    P_final = sum(coef * x ** i for i, coef in enumerate(num_coeffs))
    Q_final = sum(coef * x ** i for i, coef in enumerate(den_coeffs))

    # Return the simplified rational function
    return sp.simplify(P_final / Q_final)


def Pade_and_Taylor(func, x, m, n):

    n_exponent = n+m + 1
    # Make the Taylor approximation
    taylor = my_Taylor(func, x, n_exponent)
    # Extract my_Taylor's result
    series = [taylor.coeff(x, i) for i in range(n_exponent)]

    # Call pade
    pade_approx = pade_approximation_function(series, m, n)

    return pade_approx


def DisplayPadeTable():

    x = sp.Symbol('x')
    func = sp.exp(-x)
    max_order = 3

    print("Padé Table for e^(-x):")
    print("=" * 60)

    for m in range(max_order + 1):
        for n in range(max_order + 1):
            approx = Pade_and_Taylor(func, x, m, n)
            # It didnt work with pd dataframes, so here is as rendered LaTeX
            display(Math(f'[{m}/{n}] = ' + sp.latex(approx)))
        print("—" * 60)


def plot_ln():
    x = sp.Symbol('x')

    # First compute Taylor of ln(1+x)
    ln_taylor = my_Taylor(sp.log(1 + x), x, 21)  # 21 for a*x^20
    '''
    Now if we divide by x, every coef shifts
    x - x^2/2 + x^3/3 - x^4/4
    Divide by x
    --> 1 - x/2 + x^2/3 - x^3/4
    So now what was before the a_1 coef, now is the a_0 coef,
    Thus we need the a_{k+1}, to get the a_k coef.
    '''
    series = [ln_taylor.coeff(x, k + 1) for k in range(20)]

    # 20th order Taylor polynomial of ln(1+x)/x
    taylor_poly = sum(coef * x**i for i, coef in enumerate(series))

    # Padé [3/3] approximation
    pade_approx = pade_approximation_function(series, 3, 3)

    # Lambdify for numpy evaluation
    taylor_func = sp.lambdify(x, taylor_poly, 'numpy')
    pade_func = sp.lambdify(x, pade_approx, 'numpy')

    # Plot ----------------------------------------------
    x_vals = np.linspace(-0.999, 3, 2000)

    exact = np.where(np.abs(x_vals) < 1e-10, 1.0, np.log(1 + x_vals) / x_vals)  # Not defined at 0, but the lim x->0 is 1
    taylor_vals = np.clip(taylor_func(x_vals), -3, 3)
    pade_vals = np.clip(pade_func(x_vals), -3, 3)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_vals, exact,       'k-',  label=r'$\ln(1+x)/x$',  linewidth=5, zorder=1)
    ax.plot(x_vals, taylor_vals, 'y--', label=r'Taylor $T_{20}$', linewidth=1.5, zorder=3)
    ax.plot(x_vals, pade_vals,   'r-.', label=r'Padé $[3/3]$',   linewidth=2.5, zorder=2)

    ax.set_xlim(-1, 3)
    ax.set_ylim(-1, 2)
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)

    ax.set_title(r'\textbf{Approximations of $\ln(1+x)/x$ on $x \in (-1,\, 3)$}', size=20)
    ax.set_xlabel(r'\textsc{x}', size=16)
    ax.set_ylabel(r'\textsc{y}', size=16)

    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    y = sp.symbols('y')

    res = my_Taylor(sp.exp(-2*y), y, 7)  # 'x' for it was used for Taylor func, although it doesn't matter
    display(res)
    print('—'*50 + '\n')

    DisplayPadeTable()

    SetTex()
    plot_ln()
    print(r'Értelmezés: Nagyjából $x=0.8$-nál a $T_{20}$-as közelítés '
          r'letér a függvényről, míg a Padé közelítés végig páylán marad.'
          r'Tehát ha $x<1-re a Taylor polinom tökéletes,'
          r'Viszont $x>1$-re a $T_{20}$ teljesen öszeomlik, így marad a Padé.')
