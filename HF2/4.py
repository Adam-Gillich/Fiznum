import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy.integrate as sciint
import time


# -------------------------------------------
# Requested Functions
# -------------------------------------------


def rho_xy(x: float, y: float, rho0: float, alpha: float) -> float:
    """
    The requested rho function. Computes the density at given x, y.
    :param x: x coordinate
    :param y: y coordinate
    :param rho0: Base surface mass density
    :param alpha: Inhomogeneity parameter
    :return: The computed density at given x, y points.
    """

    return float(rho0 * (1 + alpha * (x**2 + y**2)))


def mass_cart(R: float, rho0: float, alpha: float):
    """
    The requested mass function. This calculates the
    mass using x and y, Cartesian coordinates.
    The integration bounds for x is [-R, R], and
    for y it is [y_lower, y_upper] respectively.
    :param R: Radius of the disk
    :param rho0: Base surface mass density
    :param alpha: Inhomogeneity parameter
    :return: The result and error of dblquad
    """

    def y_lower(x):
        return -np.sqrt(R**2 - x**2)

    def y_upper(x):
        return np.sqrt(R**2 - x**2)

    def integrand(y, x):
        return rho_xy(x, y, rho0, alpha)

    M, err = sciint.dblquad(integrand, -R, R, y_lower, y_upper)

    return M, err


def Iz_cart(R: float, rho0: float, alpha: float):
    """
    The requested Iz function. This calculates the
    moment of inertia, with Cartesian coordinates x, y.
    The integration bounds for x is [-R, R], and
    for y it is [y_lower, y_upper] respectively.
    :param R: Radius of the disk
    :param rho0: Base surface mass density
    :param alpha: Inhomogeneity parameter
    :return: The result and error of dblquad
    """

    def integrand(y, x, rho0, alpha):
        return (x**2 + y**2) * rho_xy(x, y, rho0, alpha)

    def y_lower(x):
        return -np.sqrt(R**2 - x**2)

    def y_upper(x):
        return np.sqrt(R**2 - x**2)

    Iz, err = sciint.dblquad(integrand, -R, R, y_lower, y_upper, args=(rho0, alpha))

    return Iz, err


def mass_polar(R: float, rho0: float, alpha: float):
    """
    The requested mass function. This calculates
    the mass using polar coordinates, where we skip
    the integration of 'phi', and assume it is 2*pi.
    Thus leaving us with 'r', for which the bounds are [0, R]
    :param R: Radius of the disk
    :param rho0: Base surface mass density
    :param alpha: Inhomogeneity parameter
    :return: The result and error of quad
    """

    def integrand(r):
        return rho0 * (1 + alpha * r**2) * r

    res, err = sciint.quad(integrand, 0, R)

    M = 2 * np.pi * res
    err = 2 * np.pi * err

    return M, err


def Iz_polar(R: float, rho0: float, alpha: float):
    """
    The requested Iz function. This calculates
    the moment of inertia using polar coordinates, where we skip
    the integration of 'phi', and assume it is 2*pi.
    Thus leaving us with 'r', for which the bounds are [0, R]
    :param R: Radius of the disk
    :param rho0: Base surface mass density
    :param alpha: Inhomogeneity parameter
    :return: The result and error of quad
    """

    def integrand(r):
        return r**2 * rho0 * (1 + alpha * r**2) * r

    res, err = sciint.quad(integrand, 0, R)

    Iz = 2 * np.pi * res
    err = 2 * np.pi * err

    return Iz, err


# -------------------------------------------
# SetTex
# -------------------------------------------


def SetTex():
    """
    Sets TeX fonts.
    """

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


def compute_all(R: float, rho0: float, alpha_arr):
    """
    Computes mass, moment of inertia, errors, and timing for every alpha value,
    using both Cartesian and polar methods.
    :param R: Radius of the disk
    :param rho0: Base surface mass density
    :param alpha_arr: Array of alpha values
    :return: Dictionary with all computed arrays
    """

    n = len(alpha_arr)

    M_c     = np.empty(n)
    M_p     = np.empty(n)
    Iz_c    = np.empty(n)
    Iz_p    = np.empty(n)
    M_c_err  = np.empty(n)
    M_p_err  = np.empty(n)
    Iz_c_err = np.empty(n)
    Iz_p_err = np.empty(n)
    t_cart  = np.empty(n)
    t_polar = np.empty(n)

    for i, alpha in enumerate(alpha_arr):
        # Mass
        M_p[i], M_p_err[i] = mass_polar(R, rho0, alpha)
        M_c[i], M_c_err[i] = mass_cart(R, rho0, alpha)

        # Iz — Cartesian (timed)
        t0 = time.perf_counter()
        Iz_c[i], Iz_c_err[i] = Iz_cart(R, rho0, alpha)
        t_cart[i] = time.perf_counter() - t0

        # Iz — polar (timed)
        t0 = time.perf_counter()
        Iz_p[i], Iz_p_err[i] = Iz_polar(R, rho0, alpha)
        t_polar[i] = time.perf_counter() - t0

    return {
        "M_c": M_c, "M_p": M_p,
        "Iz_c": Iz_c, "Iz_p": Iz_p,
        "M_c_err": M_c_err, "M_p_err": M_p_err,
        "Iz_c_err": Iz_c_err, "Iz_p_err": Iz_p_err,
        "t_cart": t_cart, "t_polar": t_polar,
    }

# -------------------------------------------
# Calculations
# -------------------------------------------


class Calculate:
    """This class makes the calculation of mass and moment of inertia."""

    def __init__(self, R, rho0, alpha_data):
        # Initialization constants
        self.R = R
        self.rho0 = rho0
        self.alpha_data = alpha_data
        # ------------------------

        n = len(self.alpha_data)

        # Data
        self.M_c = np.empty(n)
        self.M_p = np.empty(n)
        self.Iz_c = np.empty(n)
        self.Iz_p = np.empty(n)
        self.M_c_err = np.empty(n)
        self.M_p_err = np.empty(n)
        self.Iz_c_err = np.empty(n)
        self.Iz_p_err = np.empty(n)
        self.t_cart = np.empty(n)
        self.t_polar = np.empty(n)

        # ------------------------

        self.main()

    def rho_xy(self, x: float, y: float, alpha: float) -> float:
        """
        The class version of rho function. Computes the density at given x, y.
        :param x: x coordinate
        :param y: y coordinate
        :param self.rho0: Base surface mass density
        :param alpha: Inhomogeneity parameter
        :return: The computed density at given x, y points.
        """

        return float(self.rho0 * (1 + alpha * (x ** 2 + y ** 2)))

    def mass_cart(self, alpha: float) -> tuple:
        """
        he class version of mass function. This calculates the
        mass using x and y, Cartesian coordinates.
        The integration bounds for x is [-R, R], and
        for y it is [y_lower, y_upper] respectively.
        :param self.R: Radius of the disk
        :param self.rho0: Base surface mass density
        :param alpha: Inhomogeneity parameter
        :return: The result and error of dblquad
        """

        def y_lower(x):
            return -np.sqrt(self.R ** 2 - x ** 2)

        def y_upper(x):
            return np.sqrt(self.R ** 2 - x ** 2)

        def integrand(y, x):
            return self.rho_xy(x, y, alpha)

        M, err = sciint.dblquad(integrand, -self.R, self.R, y_lower, y_upper)

        return M, err

    def Iz_cart(self, alpha: float) -> tuple:
        """
        he class version of Iz function. This calculates the
        moment of inertia, with Cartesian coordinates x, y.
        The integration bounds for x is [-R, R], and
        for y it is [y_lower, y_upper] respectively.
        :param self.R: Radius of the disk
        :param self.rho0: Base surface mass density
        :param alpha: Inhomogeneity parameter
        :return: The result and error of dblquad
        """

        def integrand(y, x):
            return (x ** 2 + y ** 2) * self.rho_xy(x, y, alpha)

        def y_lower(x):
            return -np.sqrt(self.R ** 2 - x ** 2)

        def y_upper(x):
            return np.sqrt(self.R ** 2 - x ** 2)

        Iz, err = sciint.dblquad(integrand, -self.R, self.R, y_lower, y_upper)

        return Iz, err

    def mass_polar(self, alpha: float) -> tuple:
        """
        he class version of mass function. This calculates
        the mass using polar coordinates, where we skip
        the integration of 'phi', and assume it is 2*pi.
        Thus leaving us with 'r', for which the bounds are [0, R]
        :param self.R: Radius of the disk
        :param self.rho0: Base surface mass density
        :param alpha: Inhomogeneity parameter
        :return: The result and error of quad
        """

        def integrand(r):
            return self.rho0 * (1 + alpha * r ** 2) * r

        res, err = sciint.quad(integrand, 0, self.R)

        M = 2 * np.pi * res
        err = 2 * np.pi * err

        return M, err

    def Iz_polar(self, alpha: float) -> tuple:
        """
        he class version of Iz function. This calculates
        the moment of inertia using polar coordinates, where we skip
        the integration of 'phi', and assume it is 2*pi.
        Thus leaving us with 'r', for which the bounds are [0, R]
        :param self.R: Radius of the disk
        :param self.rho0: Base surface mass density
        :param alpha: Inhomogeneity parameter
        :return: The result and error of quad
        """

        def integrand(r):
            return r ** 2 * self.rho0 * (1 + alpha * r ** 2) * r

        res, err = sciint.quad(integrand, 0, self.R)

        Iz = 2 * np.pi * res
        err = 2 * np.pi * err

        return Iz, err

    def main(self):
        """
        Computes mass, moment of inertia, errors, and timing for every alpha value,
        using both Cartesian and polar methods.
        :param self.R: Radius of the disk
        :param self.rho0: Base surface mass density
        :param self.alpha_data: Array of alpha values
        :return: Dictionary with all computed arrays
        """

        for i, alpha in enumerate(self.alpha_data):
            # Mass
            self.M_p[i], self.M_p_err[i] = self.mass_polar(alpha)
            self.M_c[i], self.M_c_err[i] = self.mass_cart(alpha)

            # Iz — Cartesian (timed)
            t0 = time.perf_counter()
            self.Iz_c[i], self.Iz_c_err[i] = self.Iz_cart(alpha)
            self.t_cart[i] = time.perf_counter() - t0

            # Iz — polar (timed)
            t0 = time.perf_counter()
            self.Iz_p[i], self.Iz_p_err[i] = self.Iz_polar(alpha)
            self.t_polar[i] = time.perf_counter() - t0


def GetData(R, rho0, alpha_data):
    """
    This function only initializes the class,
    thus making its results easier to handle.
    :param R: Radius of the disk
    :param rho0: Base surface mass density
    :param alpha_data: Array of alpha values
    :return: The results of the computations
    """

    cal = Calculate(R, rho0, alpha_data)
    return vars(cal)

# -------------------------------------------
# Plotting Functions
# -------------------------------------------


def plot_Iz_over_MR2(alpha_data, data, R):
    """
    Plots I_z / MR^2 as a function of alpha. With both methods.
    :param alpha_data: Array of alpha values
    :param data: Dictionary of results
    :param R: Radius of the disk
    """

    ratio_cart = data["Iz_c"] / (data["M_c"] * R**2)
    ratio_polar = data["Iz_p"] / (data["M_p"] * R**2)

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(alpha_data, ratio_cart, '-', color='steelblue', label="Cartesian (dblquad)", linewidth=1.5)
    ax.plot(alpha_data, ratio_polar, '--', color='indianred', label="Polar (quad)", linewidth=1.5)

    # Mark alpha=0: homogeneous disk gives Iz/(MR^2) = 1/2
    ax.axhline(0.5, color='steelblue', linestyle=':', linewidth=0.8, label=r"$1/2$ (homogeneous disk)")
    ax.axvline(0.0, color='steelblue', linestyle=':', linewidth=0.8)

    ax.set_xlabel(r"$\alpha$", fontsize=12)
    ax.set_ylabel(r"$I_z / (M R^2)$", fontsize=12)
    ax.set_title(r"$I_z / (M R^2)$ as a function of $\alpha$", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_accuracy(alpha_data, data):
    """
    Plots the accuracy of the computations.
    On the left: the difference between the methods.
    On the right: the errors from quad and dblquad.
    :param alpha_data: Array of alpha values
    :param data: Dictionary of results
    """

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Accuracy comparison: Cartesian vs. polar", fontsize=13)

    # Left: absolute difference
    diff_M = np.abs(data["M_c"] - data["M_p"])
    diff_Iz = np.abs(data["Iz_c"] - data["Iz_p"])

    ax1.semilogy(alpha_data, diff_M, '-', color='steelblue', label=r"$|M_\mathrm{cart} - M_\mathrm{polar}|$")
    ax1.semilogy(alpha_data, diff_Iz, '-', color='indianred', label=r"$|I_{z,\mathrm{cart}} - I_{z,\mathrm{polar}}|$")
    ax1.set_xlabel(r"$\alpha$", fontsize=12)
    ax1.set_ylabel("Absolute difference", fontsize=12)
    ax1.set_title("Difference between methods", fontsize=12)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Right: integration errors
    ax2.semilogy(alpha_data, data["M_c_err"], '-', color='steelblue', label=r"$M$ — dblquad")
    ax2.semilogy(alpha_data, data["Iz_c_err"], '-', color='indianred', label=r"$I_z$ — dblquad")
    ax2.semilogy(alpha_data, data["M_p_err"], '--', color='steelblue', label=r"$M$ — quad")
    ax2.semilogy(alpha_data, data["Iz_p_err"], '--', color='indianred', label=r"$I_z$ — quad")
    ax2.set_xlabel(r"$\alpha$", fontsize=12)
    ax2.set_ylabel("Estimated integration error", fontsize=12)
    ax2.set_title("Integration error (reported by scipy)", fontsize=12)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_timing(alpha_data, data):
    """
    Plots the computation time of I_z for both methods as a function of alpha.
    :param alpha_data: Array of alpha values
    :param data: Dictionary of results
    """

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(alpha_data, data["t_cart"], '-', color='steelblue', label="Cartesian (dblquad)", linewidth=1.2)
    ax.plot(alpha_data, data["t_polar"], '-', color='indianred', label="Polar (quad)", linewidth=1.2)

    ax.set_xlabel(r"$\alpha$", fontsize=12)
    ax.set_ylabel("Computation time (s)", fontsize=12)
    ax.set_title(r"$I_z$ computation time vs. $\alpha$", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


# -------------------------------------------


if __name__ == "__main__":
    SetTex()

    # Parameters
    R = 1.0
    rho0 = 1.0
    alpha_data = np.linspace(-0.9, 1.0, 200)

    #data = compute_all(R, rho0, alpha_data)

    data = GetData(R, rho0, alpha_data)

    # Plot 1: Iz / (M R^2) vs alpha
    plot_Iz_over_MR2(alpha_data, data, R)

    # Interpretation for alpha = 0
    print(
        "Interpretation (alpha = 0):\n"
        "At alpha = 0 the density is homogeneous, rho(x,y) = rho0.\n"
        "The standard result gives I_z = (1/2) * M * R^2 for a homogeneous disk.\n"
        "From the plot, I_z / (M R^2) = 0.5 at alpha = 0, which confirms the formula.\n"
    )

    # Plot 2: Accuracy comparison
    plot_accuracy(alpha_data, data)

    # Plot 3: Timing comparison
    plot_timing(alpha_data, data)

    # Interpretation for timing
    print(
        "Interpretation (timing):\n"
        "The polar coordinate method (quad) is significantly faster than the Cartesian\n"
        "method (dblquad), because the angular integral was computed analytically (factor 2*pi),\n"
        "reducing the problem to a single 1D integral instead of a full 2D integration.\n"
    )
