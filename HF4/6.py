import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import sympy as sp
from IPython.display import display, Math


# ----------------------------------
# Helper functions
# ----------------------------------


def SetTex():
    """
    Sets TeX fonts.
    """

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


def Build_r(t):
    """
    Builds the spaceship's position vector r(t) symbolically.
    All rational numbers are written with sp.Rational so the
    expression remains exact.
    :param t: sympy time symbol
    :return: sympy Matrix [r_x(t), r_y(t)]
    """

    sqrt2 = sp.sqrt(2)
    sqrt3 = sp.sqrt(3)

    half = sp.Rational(1, 2)
    quarter = sp.Rational(1, 4)
    s64 = sp.Rational(1, 64)

    rx = (-sqrt2 * t / 2
          + sqrt3 * (half - t**2 * quarter)
          - (sqrt2 - 1) * (t / 2 + s64) * sp.exp(-64 * t)
          + (sqrt2 - 1) * s64)

    ry = (-t**2 * quarter
          + sqrt3 * (sqrt2 * t / 2
                     + (sqrt2 - 1) * (t / 2 + s64) * sp.exp(-64 * t)
                     - (sqrt2 - 1) * s64)
          + half)

    return sp.Matrix([rx, ry])


# ----------------------------------
# Calculate and Display functions
# ----------------------------------

def Acceleration(r, t):
    """
    Computes the acceleration vector a(t) = d^2 r / dt^2.
    :param r: position vector
    :param t: time symbol
    :return: sympy Matrix
    """

    acc = sp.simplify(sp.diff(r, t, 2))

    print('—' * 60)
    print('Acceleration vector a(t):')
    display(Math(r'\mathbf{a}(t) = ' + sp.latex(acc)))

    return acc


def GravityAtOrigin(r, t, Print=False):
    """
    Approximates the gravitational force on the spaceship by its
    value at the starting point, with the given formula:
        F_g(r(0)) = -r(0) / |r(0)|^3
    The constants mu, standard gravitational parameter of Earth,
    and m, the mass, are unity in the chosen unit system,
    so they do not appear in the formula.
    :param r: position vector
    :param t: time symbol
    :return: sympy Matrix
    """

    r0 = r.subs(t, 0)
    r0_norm = sp.sqrt((r0.T * r0)[0, 0])
    F_grav = sp.simplify(-r0 / r0_norm**3)

    if Print:
        print('—' * 60)
        print('Gravitational force at r(0):')
        display(Math(r'\mathbf{F}_g\!\left(\mathbf{r}(0)\right) = ' + sp.latex(F_grav)))

    return F_grav


def Thrust(a, F_g):
    """
    Calculates thrust.
    :param a: acceleration vector
    :param F_g: constant gravity at r(0)
    :return: 2x1 sympy Matrix
    """

    thrust = sp.simplify(a - F_g)

    print('—' * 60)
    print('Thrust vector F(t):')
    display(Math(r'\mathbf{F}(t) = ' + sp.latex(thrust)))

    return thrust


def ThrustMagnitude(F, t):
    """
    Magnitude of the thrust as a single sympy expression in t.
    :param F: thrust vector
    :param t: time symbol
    :return: scalar sympy expression
    """

    sq = sp.simplify((F.T * F)[0, 0])
    F_magni = sp.simplify(sp.sqrt(sq))

    print('—' * 60)
    print('Magnitude of the thrust |F(t)|:')
    display(Math(r'|\mathbf{F}(t)| = ' + sp.latex(F_magni)))

    return F_magni


def find_thrust_max(F_mag, t):
    """
    Locates the maximum of |F(t)| by solving d|F|/dt = 0 and
    substituting the obtained critical point back into |F|.
    :param F_mag: magnitude of the thrust as a function of t
    :param t: time symbol
    :return: (t_max, |F|_max), both sympy expressions
    """

    dF = sp.diff(F_mag, t)
    candidates = sp.solve(dF, t)

    real_pos = []
    for c in candidates:
        cs = sp.simplify(c)
        try:
            if float(cs) >= 0:
                real_pos.append(cs)
        except (TypeError, ValueError):
            continue

    if not real_pos:
        raise ValueError("No real, non-negative critical point found.")

    best_t = max(real_pos, key=lambda c: float(F_mag.subs(t, c)))
    F_max = sp.simplify(F_mag.subs(t, best_t))

    # Print results -------------------------------------------------
    print('—' * 60)
    print('Maximum of the thrust:')
    display(Math(r't_{\max} = ' + sp.latex(best_t)))
    display(Math(r'|\mathbf{F}|_{\max} = ' + sp.latex(F_max)))
    print(f'    numerical: t_max = {float(best_t):.6f},  '
          f'|F|_max = {float(F_max):.6f}')

    return best_t, F_max


# ----------------------------------
# Plot
# ----------------------------------


def plot_thrust(F_mag, t, t_max):
    """
    Plots |F(t)| from t = 0 up to roughly 5 * t_max so that
    the maximum is well visible.
    :param F_mag: magnitude of the thrust
    :param t: time symbol
    :param t_max: location of the maximum (sympy)
    """

    f = sp.lambdify(t, F_mag, 'numpy')

    upper = 5 * float(t_max)
    t_vals = np.linspace(0, upper, 1500)
    F_vals = f(t_vals)

    # Plot ----------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(t_vals, F_vals, 'b-', linewidth=2, label=r'$|\mathbf{F}(t)|$')
    ax.axvline(float(t_max), color='tomato', linestyle='--', linewidth=1.5,
               label=rf'$t_{{\max}}={float(t_max):.4f}$')

    ax.set_title(r'\textbf{Magnitude of the engine thrust over time}', size=20)
    ax.set_xlabel(r'\textsc{time}', size=16)
    ax.set_ylabel(r'$|\mathbf{F}(t)|$', size=16)

    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=14)
    plt.tight_layout()
    plt.show()


# ----------------------------------
# Main
# ----------------------------------

if __name__ == '__main__':
    t = sp.Symbol('t', positive=True)

    r = Build_r(t)

    # 1. Acceleration vector ----------------------------------
    a = Acceleration(r, t)

    # 2. Gravity at r(0) and thrust ---------------------------
    F_g = GravityAtOrigin(r, t, Print=True)

    F = Thrust(a, F_g)

    # 3. Thrust magnitude -------------------------------------
    F_mag = ThrustMagnitude(F, t)

    # 4. Maximum of the thrust --------------------------------
    t_max, F_max = find_thrust_max(F_mag, t)

    # Plot ----------------------------------------------------
    SetTex()
    plot_thrust(F_mag, t, t_max)
