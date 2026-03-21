import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


# -------------------------------------------------------
# Constants
# -------------------------------------------------------

N = 80
T1 = 1


# -------------------------------------------------------
# Requested Functions
# -------------------------------------------------------


def build_matrix(N, t1, t2, g, eta):
    """
    Makes the requested N×N matrix, with the required parameters.
    :param N: Size of the matrix
    :param t1: First-neighbour hopping amplitude
    :param t2: Second-neighbour hopping amplitude
    :param g: Non-Hermiticity parameter
    :param eta: Boundary condition parameter (0 = open, 1 = periodic)
    :return: The H matrix
    """

    # First-neighbour diagonals
    upper1 = np.full(N - 1, t1 * np.exp(g))
    lower1 = np.full(N - 1, t1 * np.exp(-g))

    # Second-neighbour diagonals
    upper2 = np.full(N - 2, t2 * np.exp(2 * g))
    lower2 = np.full(N - 2, t2 * np.exp(-2 * g))

    H = (np.diag(upper1, k=1) + np.diag(lower1, k=-1) +
         np.diag(upper2, k=2) + np.diag(lower2, k=-2))

    # Periodic boundary terms (corners)
    # First-neighbour wrapping
    H[N - 1, 0] += eta * t1 * np.exp(g)
    H[0, N - 1] += eta * t1 * np.exp(-g)

    # Second-neighbour wrapping
    H[N - 2, 0] += eta * t2 * np.exp(2 * g)
    H[0, N - 2] += eta * t2 * np.exp(-2 * g)
    H[N - 1, 1] += eta * t2 * np.exp(2 * g)
    H[1, N - 1] += eta * t2 * np.exp(-2 * g)

    return H


# -------------------------------------------------------
# Helper Functions
# -------------------------------------------------------


def eigenvalues(N, t1, t2, g, eta):
    """
    Calculates the eigen values of an H matrix defined by the list of
    parameters below, and created by 'build_matrix' function.
    :param N: Size of the matrix
    :param t1: First-neighbour hopping amplitude
    :param t2: Second-neighbour hopping amplitude
    :param g: Non-Hermiticity parameter
    :param eta: Boundary condition parameter (0 = open, 1 = periodic)
    :return: Array of the eigen values of H
    """

    H = build_matrix(N, t1, t2, g, eta)
    return np.linalg.eigvals(H)


def eigenvector_max_imag(N, t1, t2, g, eta):
    """
    This function is for the last plot. This finds the biggest eigenvalue, and it's eigen vector
    :param N: Size of the matrix
    :param t1: First-neighbour hopping amplitude
    :param t2: Second-neighbour hopping amplitude
    :param g: Non-Hermiticity parameter
    :param eta: Boundary condition parameter (0 = open, 1 = periodic)
    :return: The biggest eigenvalue, the list of psi eigenvectors attached to it
    """

    H = build_matrix(N, t1, t2, g, eta)
    vals, vecs = np.linalg.eig(H)

    if np.all(np.abs(vals.imag) < 1e-10):
        index = np.argmax(vals.real)
    else:
        index = np.argmax(vals.imag)

    lamda = vals[index]
    psi = vecs[:, index]

    norm = np.sqrt(np.sum(np.abs(psi) ** 2))
    psi = psi / norm

    return lamda, psi


def spectral_widths(N, t1, t2, g_array, eta):
    """
    Computes real and imaginary spectral widths W_Re and W_Im for each g value.
    :param N: Size of the matrix
    :param t1: First-neighbour hopping amplitude
    :param t2: Second-neighbour hopping amplitude
    :param g: Non-Hermiticity parameter
    :param eta: Boundary condition parameter (0 = open, 1 = periodic)
    :return: Width of real component (W_Re, array), width of imaginary component (W_Im, array)
    """

    W_Re = np.empty(len(g_array))
    W_Im = np.empty(len(g_array))

    for i, g in enumerate(g_array):
        eigs = eigenvalues(N, t1, t2, g, eta)
        W_Re[i] = np.max(eigs.real) - np.min(eigs.real)
        W_Im[i] = np.max(eigs.imag) - np.min(eigs.imag)

    return W_Re, W_Im


# -------------------------------------------------------
# Plotting Functions
# -------------------------------------------------------


def SetTex():
    """
    Sets TeX fonts.
    """

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


def plot_spectrum_eta(N, t1, t2, g, eta_list, eta_list2: list = None):
    """
    Plots the eigenvalue in the complex plane for several eta values.
    :param N: Size of the matrix
    :param t1: First-neighbour hopping amplitude
    :param t2: Second-neighbour hopping amplitude
    :param g: Non-Hermiticity parameter
    :param eta_list: List of eta values to visualise
    :param eta_list2: Second list of eta values to visualise
    """

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title(rf"Spectrum for $t_2={t2},\; g={g}$, with varying $\eta$", fontsize=13)
    ax.set_xlabel(r"$\mathrm{Re}(\lambda)$", fontsize=12)
    ax.set_ylabel(r"$\mathrm{Im}(\lambda)$", fontsize=12)

    for eta in eta_list:
        eigs = eigenvalues(N, t1, t2, g, eta)
        ax.scatter(eigs.real, eigs.imag, s=12, label=rf"$\eta = {eta}$")

    if isinstance(eta_list2, list):
        for eta in eta_list2:
            eigs = eigenvalues(N, t1, t2, g, eta)
            ax.scatter(eigs.real, eigs.imag, s=12, label=rf"$\eta = {eta}$")

    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_spectral_widths(N, t1, t2, g_array):
    """
    Plots W_Re(g) and W_Im(g) for open (eta=0) and periodic (eta=1) eta.
    :param N: Size of the matrix
    :param t1: First-neighbour hopping amplitude
    :param t2: Second-neighbour hopping amplitude
    :param g_array: Array of g values.
    """

    W_Re_open, W_Im_open = spectral_widths(N, t1, t2, g_array, eta=0)
    W_Re_periodic,  W_Im_periodic = spectral_widths(N, t1, t2, g_array, eta=1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(rf"Spectral widths vs $g$ for $t_2={t2}$", fontsize=13)

    # W_Re
    ax1.plot(g_array, W_Re_open, '-o', markersize=3, label=r"$\eta=0$ (open)")
    ax1.plot(g_array, W_Re_periodic,  '-s', markersize=3, label=r"$\eta=1$ (periodic)")
    ax1.set_xlabel(r"$g$", fontsize=12)
    ax1.set_ylabel(r"$W_{\mathrm{Re}}$", fontsize=12)
    ax1.set_title(r"Real width $W_{\mathrm{Re}}(g)$", fontsize=12)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # W_Im
    ax2.plot(g_array, W_Im_open, '-o', markersize=3, label=r"$\eta=0$ (open)")
    ax2.plot(g_array, W_Im_periodic,  '-s', markersize=3, label=r"$\eta=1$ (periodic)")
    ax2.set_xlabel(r"$g$", fontsize=12)
    ax2.set_ylabel(r"$W_{\mathrm{Im}}$", fontsize=12)
    ax2.set_title(r"Imaginary width $W_{\mathrm{Im}}(g)$", fontsize=12)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_spectrum_t2(N, t1, g, eta, t2_list):
    """
    Plots the eigenvalue spectrum in the complex plane for several t2 values.
    :param N: Size of the matrix
    :param t1: First-neighbour hopping amplitude
    :param g: Non-Hermiticity parameter
    :param eta: Boundary condition parameter (0 = open, 1 = periodic)
    :param t2_list: List of t2 values
    """

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title(rf"Spectrum for $g={g},\; \eta={eta}$, with varying $t_2$", fontsize=13)
    ax.set_xlabel(r"$\mathrm{Re}(\lambda)$", fontsize=12)
    ax.set_ylabel(r"$\mathrm{Im}(\lambda)$", fontsize=12)

    for t2 in t2_list:
        eigs = eigenvalues(N, t1, t2, g, eta)
        ax.scatter(eigs.real, eigs.imag, s=12, label=rf"$t_2 = {t2}$", zorder=3)

    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_eigenvector_comparison(N, t1, t2, g):
    """
    This plots the squared absolute value of the indices of the eigenfunctions as a function of the indices (n).
    :param N: Size of the matrix
    :param t1: First-neighbour hopping amplitude
    :param t2: Second-neighbour hopping amplitude
    :param g: Non-Hermiticity parameter
    """

    lamda_open, psi_open = eigenvector_max_imag(N, t1, t2, g, eta=0)
    lamda_periodic,  psi_periodic = eigenvector_max_imag(N, t1, t2, g, eta=1)

    n_arr = np.arange(N)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(rf"Eigenvector with largest $\mathrm{{Im}}(\lambda)$ "
                 rf"($t_2={t2},\; g={g}$)", fontsize=13)

    ax1.bar(n_arr, np.abs(psi_open) ** 2, color='steelblue', width=1.0, edgecolor='navy', linewidth=0.3)
    ax1.set_title(rf"$\eta=0$ (open), $\lambda={lamda_open:.4f}$", fontsize=11)
    ax1.set_xlabel(r"$n$", fontsize=12)
    ax1.set_ylabel(r"$|\psi_n|^2$", fontsize=12)
    ax1.grid(True, alpha=0.3)

    ax2.bar(n_arr, np.abs(psi_periodic) ** 2, color='crimson', width=1.0, edgecolor='darkred', linewidth=0.3)
    ax2.set_title(rf"$\eta=1$ (periodic), $\lambda={lamda_periodic:.4f}$", fontsize=11)
    ax2.set_xlabel(r"$n$", fontsize=12)
    ax2.set_ylabel(r"$|\psi_n|^2$", fontsize=12)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


# -------------------------------------------------------
# Main
# -------------------------------------------------------


def main():
    """
    This is the main function, where every function is called and orchestrated to work together.
    """

    SetTex()

    # --- Task 1: Spectrum vs eta ---
    eta_list = [1e-14, 1e-10, 1e-7, 1e-3, 1]
    eta_list2 = [0.0, 0.25, 0.5, 0.75, 1.0]
    # plot_spectrum_eta(N, T1, t2=0.3, g=0.4, eta_list=eta_list, eta_list2=eta_list2)

    # --- Task 1 interpretation ---
    print(
        "Interpretation (spectrum vs eta):\n"
        "For eta=0 (open BC) the eigenvalues are all real, lying on the real axis.\n"
        "As eta increases from 0 toward 1, the spectrum gradually acquires a nonzero imaginary part,\n"
        "and the eigenvalues spread into the complex plane, forming a closed loop-like structure.\n"
        "At eta=1 (fully periodic BC) the spectrum forms a distinct closed curve in the complex plane.\n"
        "The transition is smooth: even a tiny eta > 0 already shifts some eigenvalues off the real axis,\n"
        "but the full loop only closes when the boundary coupling reaches its maximum value.\n"
    )

    # --- Task 2: Spectral widths vs g ---
    g_array = np.linspace(0, 0.8, 100)
    # plot_spectral_widths(N, T1, t2=0.3, g_array=g_array)

    # --- Task 2 interpretation ---
    print(
        "Interpretation (spectral widths vs g):\n"
        "For open BC (eta=0), W_Re grows with g while W_Im stays zero (all eigenvalues remain real).\n"
        "For periodic BC (eta=1), both W_Re and W_Im grow with g, since the spectrum expands\n"
        "in both the real and imaginary directions as the non-Hermiticity increases.\n"
        "The real width behaves similarly in both cases, but the imaginary width is dramatically\n"
        "different: it is identically zero for open BC, but increases steadily for periodic BC.\n"
    )

    # --- Task 3: Spectrum vs t2 ---
    t2_list = [0.0, 0.1, 0.2, 0.3, 0.4]
    # plot_spectrum_t2(N, T1, g=0.4, eta=1, t2_list=t2_list)

    # --- Task 3 interpretation ---
    print(
        "Interpretation (spectrum vs t2):\n"
        "At t2=0 the spectrum forms a simple ellipse in the complex plane.\n"
        "As t2 increases, the second-neighbour hopping deforms this ellipse:\n"
        "the curve acquires additional structure (lobes or figure-eight-like features),\n"
        "and the overall extent of the spectrum increases in both real and imaginary directions.\n"
        "The shape evolves from a single loop to a more complex, multi-lobed closed curve.\n"
    )

    # --- Task 4: Eigenvector comparison ---
    plot_eigenvector_comparison(N, T1, t2=0.3, g=0.4)

    # --- Task 4 interpretation ---
    print(
        "Interpretation (eigenvector comparison):\n"
        "For open BC (eta=0), |psi_n|^2 is exponentially localised toward one edge of the chain.\n"
        "This is the non-Hermitian skin effect: all eigenstates pile up at the boundary.\n"
        "For periodic BC (eta=1), |psi_n|^2 is approximately uniform across all sites,\n"
        "resembling a delocalised Bloch wave. The periodic boundary condition removes the\n"
        "preferred edge, and the eigenstates spread evenly over the entire system.\n"
    )


if __name__ == "__main__":
    main()
