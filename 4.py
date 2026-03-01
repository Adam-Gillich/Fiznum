import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


# -------------------------------------------

def TruePolynom(num_coeffs, den_coeffs, z):
    """
    Creates F = P/Q.
    :param num_coeffs: P coefficients
    :param den_coeffs: Q coefficients
    :param z: A complex number, or a numpy array.
    :return: F = P/Q, so, the divided two polynoms, with np.inf at the poles.
    """

    P = poly(num_coeffs, z)
    Q = poly(den_coeffs, z)
    # Handle division by zero for numpy arrays
    with np.errstate(divide='ignore', invalid='ignore'):
        F = np.where(Q != 0, P / Q, np.inf)
    return F


# -------------------------------------------

def poly(coeffs: list, z):
    """
    This creates and calculates the value of a polynom.
    :param coeffs: Coefficients of the polynom arranged into a list.
    :param z: A number. Could be an array.
    :return: One number, or array, that's the result of the polynom.
    """

    if isinstance(z, (float, int, complex)):
        result = 0
        for n in range(len(coeffs)):
            result += coeffs[n] * z**n
        return result

    if isinstance(z, np.ndarray):
        result = np.zeros_like(z, dtype=complex)
        for n in range(len(coeffs)):
            result += coeffs[n] * z**n
        return result

    else:
        return False


# -------------------------------------------

def SetTex():
    """
    Sets TeX fonts.
    """

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


def initials(axis, xlim, ylim, xlabel, ylabel, title, lcolor):
    """
    Creates the common parts between the two plots.
    :param axis: Current axis
    :param xlim: Limit of x-axis
    :param ylim: Limit of y-axis
    :param xlabel: Label of x
    :param ylabel: Label of y
    :param title: Title of subplot
    :param lcolor: Line color of the x,y axes
    """

    axis.set_aspect('equal')

    # Set x, y limits
    axis.set_xlim(xlim[0], xlim[1])
    axis.set_ylim(ylim[0], ylim[1])

    # Make x, y lines
    line_attributes = dict(color=lcolor, linestyle='-', lw=0.5, alpha=0.7)
    axis.axhline(y=0, **line_attributes)
    axis.axvline(x=0, **line_attributes)

    # Set axis label, and title
    axis.set_xlabel(xlabel, fontsize=12)
    axis.set_ylabel(ylabel, fontsize=12)
    axis.set_title(title, fontsize=13)

    axis.grid(True, alpha=0.3)


def axis1(fig, axisI, xlim, ylim, Fz, X, Y):
    """
    Creates everything of 'ax1'. Starting with the initials, then calculating the absolute values of F(z),
    then applying logarithmic scaling for the plot.
    :param fig: Main fig
    :param axisI: 'ax1'
    :param xlim: Limit of x-axis
    :param ylim: Limit of y-axis
    :param Fz: The F(z) function.
    :param X: Array from meshgrid, representing  Re(z)
    :param Y: Array from meshgrid, representing Im(z)
    """

    initials(axisI, xlim, ylim,
             r'$\mathrm{Re}(z)$', r'$\mathrm{Im}(z)$',
             r'Absolute value $|F(z)|$ (log scale)', 'red')

    # Calculate F(z) variants
    F_abs = np.abs(Fz)
    F_log = np.log10(F_abs + 1e-10)  # To avoid log(0) -> +1e-10

    color_vals = axisI.pcolormesh(X, Y, F_log, cmap='gray_r', shading='auto')
    cbar = fig.colorbar(color_vals, ax=axisI)
    cbar.set_label(r'$\log_{10}|F(z)|$', fontsize=12)


def axis2(fig, axisII, xlim, ylim, Fz, X, Y):
    """
    Creates everything of 'ax2'. Starting with the initials, then calculating the phase angle of F(z), and using the
    cyclic colormap 'twilight' to plot the values.
    :param fig: Main fig
    :param axisII: 'ax2'
    :param xlim: Limit of x-axis
    :param ylim: Limit of y-axis
    :param Fz: The F(z) function values
    :param X: Array from meshgrid, representing  Re(z)
    :param Y: Array from meshgrid, representing Im(z)
    """

    initials(axisII, xlim, ylim,
             r'$\mathrm{Re}(z)$', r'$\mathrm{Im}(z)$',
             r'Phase angle $\arg(F(z))$', 'white')

    # Calculate F(z) phase angle
    F_phase = np.angle(Fz)

    color_vals = axisII.pcolormesh(X, Y, F_phase, cmap='twilight', shading='auto', vmin=-np.pi, vmax=np.pi)
    cbar = fig.colorbar(color_vals, ax=axisII)
    cbar.set_label(r'$\arg(F(z))$ [rad]', fontsize=12)


def plot_complex_rational(num_coeffs, den_coeffs, xlim=(-10, 10), ylim=(-10, 10), n=200):
    """
    Main plotting function, plots everything.
    :param num_coeffs: Coefficients of numerator (P)
    :param den_coeffs: Coefficients of denominator (Q)
    :param xlim: Limit of x-axis
    :param ylim: Limit of y-axis
    :param n: Number of sample points
    """

    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))

    # Create meshgrid
    x = np.linspace(xlim[0], xlim[1], n)
    y = np.linspace(ylim[0], ylim[1], n)
    X, Y = np.meshgrid(x, y)
    z = X + 1j * Y

    # Calculate F(z)
    Fz = TruePolynom(num_coeffs, den_coeffs, z)

    # Plot the axes
    axis1(fig, ax1, xlim, ylim, Fz, X, Y)
    axis2(fig, ax2, xlim, ylim, Fz, X, Y)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    SetTex()

    # Example 1: F(z) = z (identity function)
    # Zeros: z = 0
    print("Example 1: F(z) = z")
    plot_complex_rational([0, 1], [1], xlim=(-5, 5), ylim=(-5, 5))

    # Example 2: F(z) = (z-1)(z+1) / z = (z^2 - 1) / z
    # Zeros: z = ±1, Pole: z = 0
    print("\nExample 2: F(z) = (z^2 - 1) / z")
    plot_complex_rational([-1, 0, 1], [0, 1], xlim=(-3, 3), ylim=(-3, 3))

    # Example 3: F(z) = 1 / (z^2 + 1)
    # Zeros: none (real), Poles: z = ±i
    print("\nExample 3: F(z) = 1 / (z^2 + 1)")
    plot_complex_rational([1], [1, 0, 1], xlim=(-3, 3), ylim=(-3, 3))
