import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy.integrate as sciint
import scipy.interpolate as sciintp
import ipywidgets as wid

# -------------------------------------------
# Constants
# -------------------------------------------

H0 = 1.0
L0 = 1.0


# -------------------------------------------
# Calculations
# -------------------------------------------


def solve_trajectory(v0: float, h0: float = H0, l0: float = L0):
    """
    This function solves the ODE.
    :param v0: Initial horizontal velocity
    :param h0: Initial height from the metal plate
    :param l0: Initial horizontal position
    :return: OdeResult object from 'solve_ivp'
    """

    def derivatives(t: float, state: np.ndarray) -> list[float]:
        """
        This function contains the equations, and is given to 'solve_ivp'.
        :param t: Current time, required by 'solve_ivp'
        :param state: State vector [h, l, vh, vl]
        :return: Time derivatives, velocity and acceleration
        """

        h, l, vh, vl = state

        r_sq = h ** 2 + l ** 2
        r_32 = r_sq ** 1.5

        # Equations
        ah = -h / (4 * r_32) - 1 / (4 * h ** 2)
        al = -l / (4 * r_32) + 1 / (4 * l ** 2)

        return [vh, vl, ah, al]

    def hit_plate(t: float, state: np.ndarray):
        """
        This is the event function. Checks when the charge
        reaches the plate. More accurately 1e-3 from the plate.
        There the integration terminates.
        :param t: Current time, required by 'solve_ivp'
        :param state: State vector [h, l, vh, vl]
        :return: Distance from threshold (h - 1e-3)
        """

        return state[0] - 1e-3

    # If event is true, integration will stop at that threshold.
    hit_plate.terminal = True
    # Detect crossing from above (h decreasing through threshold).
    hit_plate.direction = -1

    # ------------------------------------------------------------

    # Initial state: [h, l, vh, vl]
    y0 = [h0, l0, 0.0, -v0]

    T_MAX = 50

    res = sciint.solve_ivp(derivatives, [0, T_MAX], y0,
                           events=hit_plate, dense_output=True, max_step=0.01, rtol=1e-10, atol=1e-12)

    return res


def impact_x(v0: float) -> float:
    """
    Returns the l-coordinate where the charge hits the plate for a given v0.
    :param v0: Initial horizontal velocity
    :return: The l-coordinate at the moment of impact
    """

    res = solve_trajectory(v0)

    # If the event was detected, use its l-value; otherwise use the last point.
    if res.t_events[0].size > 0:
        # Stats for nerds:
        # [0] ~1st and only event~,
        # [0] ~1st and only occurrence (since terminal)~,
        # [1] ~[1]th element of the state vector (l)~
        return res.y_events[0][0][1]
    else:
        return res.y[1, -1]


# -------------------------------------------
# Plotting Functions
# -------------------------------------------


def SetTex():
    """
    Sets TeX fonts.
    """

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


def plot_interactive(v0: float = 0.0):
    """
    This function plots the trajectory of the charges.
    And this will be the interactive plot.
    :param v0: Initial horizontal velocity
    """

    fig, ax = plt.subplots(figsize=(7, 7))

    res = solve_trajectory(v0)
    h = res.y[0]
    l = res.y[1]

    # Right charge: (+l, +h)
    ax.plot(l, h, '-', color='steelblue', label='Right charge')
    ax.plot(l[-1], h[-1], 'o', color='steelblue', markersize=8, zorder=5)

    # Right mirror charge: (+l, -h)
    ax.plot(l, -h, '--', color='cornflowerblue', alpha=0.6, label='Right mirror')
    ax.plot(l[-1], -h[-1], 'o', color='cornflowerblue', markersize=8, zorder=5)

    # Left charge: (-l, +h)
    ax.plot(-l, h, '-', color='indianred', label='Left charge')
    ax.plot(-l[-1], h[-1], 'o', color='indianred', markersize=8, zorder=5)

    # Left mirror charge: (-l, -h)
    ax.plot(-l, -h, '--', color='lightcoral', alpha=0.6, label='Left mirror')
    ax.plot(-l[-1], -h[-1], 'o', color='lightcoral', markersize=8, zorder=5)

    # Metal plate
    ax.axhline(y=0, color='gray', linewidth=2, linestyle='-', label='Metal plate')

    # Initial positions
    ax.plot(L0, H0, 's', color='navy', markersize=7, zorder=6)
    ax.plot(-L0, H0, 's', color='darkred', markersize=7, zorder=6)

    ax.set_xlabel(r'$x$', fontsize=13)
    ax.set_ylabel(r'$y$', fontsize=13)
    ax.set_title(rf'Charge trajectories for $v_0 = {v0:.2f}$', fontsize=13)
    ax.set_aspect('equal')
    ax.legend(fontsize=9, bbox_to_anchor=(1.23, 1), loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.show()


def plot_impact_vs_v0():
    """
    Plots the impact points.
    """

    # Make v0 points
    v0_data = np.linspace(-2, 2, 100)
    x_impact = np.array([impact_x(v) for v in v0_data])

    # Build a CubicSpline of (v0, x_impact - L0) and solve for zeros.
    cs = sciintp.CubicSpline(v0_data, x_impact - L0)
    v0_roots = cs.solve(0.0, extrapolate=False)

    x_at_roots = np.array([impact_x(v) for v in v0_roots])

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(v0_data, x_impact, '-', color='steelblue', linewidth=1.5, label='$x$-coordinate')
    ax.plot(v0_roots, x_at_roots, 'o', color='crimson', markersize=8, zorder=5, label=r'$x_{\mathrm{impact}} = x_0$')
    ax.axhline(y=L0, color='gray', linewidth=0.8, linestyle='--', alpha=0.7, label=f'Initial $x = {L0}$')

    ax.set_xlabel(r'$v_0$', fontsize=13)
    ax.set_ylabel(r'$x$', fontsize=13)
    ax.set_title(r'Impact $x$-coordinates', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


# -------------------------------------------
# Main
# -------------------------------------------


def main():
    """
    Orchestrates the full solution: interactive plot, sampling,
    CubicSpline root-finding, and the static summary plot.
    """

    SetTex()

    # --- Interactive plot ---
    wid.interact(plot_interactive, v0=(-2, 2, 0.01))

    # --- Observation ---
    print(
        "Observation (slider behaviour):\n"
        "For the charge to land exactly below its starting position (x_impact = x_0),\n"
        "the initial inward velocity v0 must be tuned so that the attractive force\n"
        "from the mirror charge (pulling the charge toward the plate) and the\n"
        "repulsive force from the other real charge (pushing it sideways) balance\n"
        "in such a way that the net horizontal displacement is zero over the\n"
        "entire trajectory. This happens only at specific discrete v0 values.\n"
    )

    # --- Static plot with CubicSpline analysis ---
    # plot_impact_vs_v0()


if __name__ == "__main__":
    main()
