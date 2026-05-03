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
    Configures matplotlib to render all text through LaTeX using
    the Computer Modern serif font, matching standard physics typesetting.
    Must be called before any plot is created.
    """
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


# ----------------------------------
# Analysis functions
# ----------------------------------


def ComputeDistances(r, phi):
    """
    Computes distances between the bead and each fixed charge
    in both Cartesian and polar (chord-length) form, then prints
    and displays both sets of results.
        The chord-length identity 2 - 2*cos(phi) = 4*sin^2(phi/2),
    giving the cleaner forms d1 = 2r*sin(phi/2) and d2 = 2r*cos(phi/2).
    :param r:   sympy Symbol, radius of the semicircle
    :param phi: sympy Symbol, polar angle of the bead in radians
    :return:    (d1_polar, d2_polar) — bead-to-Q1 and bead-to-Q2 distances
                as sympy expressions
    """
    # --- Cartesian ---
    d1_cart = sp.sqrt((r * sp.cos(phi) - r)**2 + (r * sp.sin(phi))**2)
    d2_cart = sp.sqrt((r * sp.cos(phi) + r)**2 + (r * sp.sin(phi))**2)

    d1_cart = sp.simplify(d1_cart)
    d2_cart = sp.simplify(d2_cart)

    # --- Polar (chord-length formula) ---
    d1_polar = 2 * r * sp.sin(phi / 2)
    d2_polar = 2 * r * sp.cos(phi / 2)

    d12 = 2 * r  # For the distance is always the diameter

    print('—' * 60)
    print('Distances (Cartesian):')
    display(Math(fr'd_1 = {sp.latex(d1_cart)}'))
    display(Math(fr'd_2 = {sp.latex(d2_cart)}'))
    display(Math(fr'd_{{12}} = {sp.latex(d12)}'))

    print('\nDistances (Polar / chord-length formula):')
    display(Math(fr'd_1 = {sp.latex(d1_polar)}'))
    display(Math(fr'd_2 = {sp.latex(d2_polar)}'))
    display(Math(fr'd_{{12}} = {sp.latex(d12)}'))

    return d1_polar, d2_polar


def ComputeForces(r, phi, Q1, Q2, q, d1, d2):
    """
    Computes the Coulomb force vectors acting on the bead from each
    fixed charge, then projects them onto the tangential direction of
    the circular arc to obtain the tangential force components.
        The tangential component of each force is the dot product with the
    tangent vector. The total tangential force F_t = F1_t + F2_t governs
    whether the bead accelerates along the arc.
    :param r:   sympy Symbol, radius
    :param phi: sympy Symbol, polar angle of the bead
    :param Q1:  sympy Symbol, charge fixed at angle 0
    :param Q2:  sympy Symbol, charge fixed at angle pi
    :param q:   sympy Symbol, charge of the sliding bead
    :param d1:  sympy expression, bead-to-Q1 distance
    :param d2:  sympy expression, bead-to-Q2 distance
    :return:    F_t — total tangential force on the bead as a sympy expression
    """
    bead = sp.Matrix([r * sp.cos(phi), r * sp.sin(phi)])
    p1 = sp.Matrix([r, 0])
    p2 = sp.Matrix([-r, 0])

    F1 = sp.simplify(Q1 * q * (bead - p1) / d1**3)
    F2 = sp.simplify(Q2 * q * (bead - p2) / d2**3)

    tangent = sp.Matrix([-sp.sin(phi), sp.cos(phi)])

    F1_t = sp.trigsimp(sp.simplify(F1.dot(tangent)))
    F2_t = sp.trigsimp(sp.simplify(F2.dot(tangent)))
    F_t = sp.trigsimp(sp.simplify(F1_t + F2_t))

    print('—' * 60)
    print('Coulomb forces on the bead (k_e = 1):')
    display(Math(fr'\mathbf{{F}}_1 = {sp.latex(F1)}'))
    display(Math(fr'\mathbf{{F}}_2 = {sp.latex(F2)}'))

    print('\nTangential components:')
    display(Math(fr'F_{{1,t}} = {sp.latex(F1_t)}'))
    display(Math(fr'F_{{2,t}} = {sp.latex(F2_t)}'))
    display(Math(fr'F_t = F_{{1,t}} + F_{{2,t}} = {sp.latex(F_t)}'))

    return F_t


def find_equilibrium_ratio(F_t, phi, Q1, Q2):
    """
    Determines the Q1/Q2 charge ratio required to place the bead in
    equilibrium at phi = 60 degrees.
        Equilibrium requires F_t = 0. We solve this by substituting
    Q1 = rho * Q2 into the equation, and solving for F_t = 0,
    thus getting rho, which is the ratio Q1/Q2.

    :param F_t: sympy expression, total tangential force on the bead
    :param phi: sympy Symbol, polar angle of the bead
    :param Q1:  sympy Symbol, charge at angle 0
    :param Q2:  sympy Symbol, charge at angle pi
    :return:    (ratio_general, ratio_60),
                ratio_general — Q1/Q2 as a function of phi,
                ratio_60      — Q1/Q2 evaluated at phi = 60°
    """
    rho = sp.Symbol('rho')

    F_sub = F_t.subs(Q1, rho * Q2)
    F_sub = sp.cancel(F_sub)

    solutions = sp.solve(F_sub, rho)
    ratio_general = sp.trigsimp(solutions[0])

    ratio_60 = sp.simplify(ratio_general.subs(phi, sp.pi / 3))

    print('—' * 60)
    print('Equilibrium condition F_t = 0  =>  Q1/Q2:')
    display(Math(fr'\frac{{Q_1}}{{Q_2}} = {sp.latex(ratio_general)}'))

    print(f'\nAt phi = 60°:')
    display(Math(fr'\frac{{Q_1}}{{Q_2}}\bigg|_{{\phi=60°}} = {sp.latex(ratio_60)} \approx {float(ratio_60):.6f}'))

    return ratio_general, ratio_60


def StabilityAnalysis(F_t, phi, Q1, Q2, q, r, ratio_60):
    """
    Determines whether the equilibrium at phi = 60° is stable or
    unstable by evaluating the derivative of F_t at that point.
    :param F_t:     sympy expression, total tangential force
    :param phi:     sympy Symbol, polar angle of the bead
    :param Q1:      sympy Symbol, charge at angle 0
    :param Q2:      sympy Symbol, charge at angle pi
    :param q:       sympy Symbol, charge of the bead
    :param r:       sympy Symbol, radius of the arc
    :param ratio_60: sympy expression, Q1/Q2 evaluated at phi = 60°
    :return:        dF_eq — derivative of F_t at phi = 60°, sympy expression
    """
    F_sub = F_t.subs(Q1, ratio_60 * Q2)
    dF = sp.diff(F_sub, phi)
    dF_eq = sp.simplify(dF.subs(phi, sp.pi / 3))

    print('—' * 60)
    print('Derivative of the tangential force at phi = 60°:')
    display(Math(fr'\frac{{dF_t}}{{d\phi}}\bigg|_{{\phi=60°}} = {sp.latex(dF_eq)}'))

    print('\nStability criterion: dF_t/dphi < 0  =>  stable equilibrium.')

    coeff = sp.simplify(dF_eq / (q * Q2 / r**2))  # So we get a numeric output
    numeric = float(coeff)

    display(Math(fr'\frac{{dF_t}}{{d\phi}}\bigg|_{{\phi=60°}} = \frac{{q\,Q_2}}{{r^2}}\,\cdot\,{sp.latex(coeff)}'))

    sign_str = 'positive' if numeric > 0 else 'negative'
    print(f'\n  Numeric factor = {numeric:.6f}  ({sign_str})')

    if numeric > 0:
        print('  => Stable  when q·Q2 < 0  (bead charge opposite to Q2)')
        print('  => Unstable when q·Q2 > 0  (bead charge same sign as Q2)')
    else:
        print('  => Stable  when q·Q2 > 0  (bead and Q2 have the same sign)')
        print('  => Unstable when q·Q2 < 0  (bead and Q2 have opposite signs)')

    return dF_eq


# ----------------------------------
# Plot
# ----------------------------------


def plot_tangential_force(F_t, phi, Q1, Q2, q, r):
    """
    Plots the magnitude of the tangential force |F_t| as a function
    of the bead angle phi with a logarithmic y-axis,
    for three different Q1/Q2 charge ratios.
    :param F_t: sympy expression, total tangential force
    :param phi: sympy Symbol, polar angle of the bead
    :param Q1:  sympy Symbol, charge at angle 0
    :param Q2:  sympy Symbol, charge at angle pi
    :param q:   sympy Symbol, charge of the bead
    :param r:   sympy Symbol, radius of the arc
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    phi_vals = np.linspace(0.1, 3.1, 2000)

    ratios = [sp.sqrt(3) / 3, sp.Integer(100), sp.Integer(1)]
    labels = [r'$Q_1/Q_2 = \sqrt{3}/3$', r'$Q_1/Q_2 = 100$', r'$Q_1/Q_2 = 1$']

    for ratio, lbl in zip(ratios, labels):
        expr = F_t.subs([(Q1, ratio), (Q2, 1), (q, 1), (r, 1)])
        expr = sp.simplify(expr)
        f_numpy = sp.lambdify(phi, expr, 'numpy')
        vals = np.abs(f_numpy(phi_vals))
        ax.semilogy(phi_vals, vals, label=lbl, linewidth=2)

    ax.set_xlabel(r'$\phi$ [rad]', size=16)
    ax.set_ylabel(r'$|F_t|$', size=16)
    ax.set_title(r'\textbf{Tangential force magnitude (log scale, stable config.)}', size=20)

    ax.legend(fontsize=14)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


# ----------------------------------
# Main
# ----------------------------------

if __name__ == '__main__':

    # 1. Define symbols ----------------------------------------
    r = sp.Symbol('r', positive=True, real=True)
    phi = sp.Symbol('phi', positive=True, real=True)
    Q1 = sp.Symbol('Q1', real=True)
    Q2 = sp.Symbol('Q2', real=True)
    q = sp.Symbol('q', real=True)
    m = sp.Symbol('m', positive=True, real=True)
    print()

    # 2. Distances in Cartesian and polar coordinates ----------
    d1, d2 = ComputeDistances(r, phi)
    print()

    # 3. Forces and tangential components ----------------------
    F_t = ComputeForces(r, phi, Q1, Q2, q, d1, d2)
    print()

    # 4. Equilibrium ratio at phi = 60° -----------------------
    ratio_general, ratio_60 = find_equilibrium_ratio(F_t, phi, Q1, Q2)
    print()

    # 5. Stability analysis ------------------------------------
    dF_eq = StabilityAnalysis(F_t, phi, Q1, Q2, q, r, ratio_60)
    print()

    # 6. Plot --------------------------------------------------
    SetTex()
    plot_tangential_force(F_t, phi, Q1, Q2, q, r)
