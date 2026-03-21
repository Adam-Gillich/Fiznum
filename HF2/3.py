import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
import scipy.sparse as scisp


# -------------------------------------------
# Requested Function
# -------------------------------------------


def nDimenziosKocka(N: int) -> scisp.csr_matrix:
    """
    This function creates the adjacency matrix of an N
    dimensional cube as a sparce matrix, recursively.
    :param N: Number of dimensions
    :return: Sparce adjacency matrix
    """

    # Base case: 1D cube is just two nodes connected by a single edge.
    if N == 1:
        return scisp.csr_matrix(np.array([[0, 1],
                                          [1, 0]]))

    # Get the (N-1)-dimensional cube's adjacency matrix
    M_prev = nDimenziosKocka(N - 1)
    size = M_prev.shape[0]

    # Prepare the identity and Pauli-X (sigma_x) matrices.
    I = scisp.identity(size, format='csr')
    sigma_x = scisp.csr_matrix(np.array([[0, 1],
                                         [1, 0]]))

    # Build M_N as the block structure: [[M_prev, I], [I, M_prev]]
    # Using: M_N = kron(I_2, M_prev) + kron(sigma_x, I_size)
    M_N = scisp.kron(scisp.identity(2, format='csr'), M_prev, format='csr') + scisp.kron(sigma_x, I, format='csr')

    return M_N


# -------------------------------------------
# Helper Functions
# -------------------------------------------


def smallest_eigenvalues(N: int, k: int = 10) -> np.ndarray:
    """
    Finds the Smallest Algebraic (SA) eigenvalues of an N
    dimensional cube's adjacency matrix, and sorts it. This
    is requested for checking if the formula works.
    :param N: Number of dimensions
    :param k: Number of smallest eigenvalues to compute
    :return: Sorted array of the ('k' number of) smallest eigenvalues
    """

    M = nDimenziosKocka(N)
    # Use 'SA' (smallest algebraic) for Hermitian solver.
    vals = scisp.linalg.eigsh(M, k=k, which='SA', return_eigenvectors=False)
    return np.sort(vals)


def measure_generation_times(max_dim: int = 22) -> tuple[list[int], list[float]]:
    """
    This function measures the generation time of the
    adjacency matrices up to 'max_dim' dimensions.
    :param max_dim: Maximum dimension to test
    :return: List of dimensions, List of generation times
    """

    dims = list(range(1, max_dim + 1))
    times = []

    for n in dims:
        t0 = time.time()
        nDimenziosKocka(n)
        t1 = time.time()
        times.append(t1 - t0)

    return dims, times


def extreme_eigenvectors(N: int):
    """
    This function finds the biggest and smallest eigenvalue
    and its eigenvector, for an N dimensional adjacency matrix.
    :param N: Dimensional of the adjacency matrix
    :return: Smallest eigenvalue, its eigenvector, Largest eigenvalue, its eigenvector
    """

    M = nDimenziosKocka(N)

    # Smallest algebraic eigenvalue
    val_min, vec_min = scisp.linalg.eigsh(M, k=1, which='SA')
    # Largest algebraic eigenvalue
    val_max, vec_max = scisp.linalg.eigsh(M, k=1, which='LA')

    return val_min[0], vec_min[:, 0], val_max[0], vec_max[:, 0]


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


def plot_timing(dims: list[int], times: list[float]):
    """
    Plots the time it takes for every adjacency matrix to generate. On a logarithmic scale.
    :param dims: List of dimensions
    :param times: List of measured times
    """

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.semilogy(dims, times, 'o-', color='steelblue', markersize=5)

    ax.set_xlabel("Dimension (N)", fontsize=12)
    ax.set_ylabel("Generation time (s)", fontsize=12)
    ax.set_title("Hypercube adjacency matrix generation time vs. dimension", fontsize=13)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_eigenvectors(N: int = 6):
    """
    Plots the eigenvector belonging to the biggest and smallest eigenvalues.
    :param N: Dimensional of the adjacency matrix
    """

    val_min, vec_min, val_max, vec_max = extreme_eigenvectors(N)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f"Eigenvectors of the {N}D hypercube adjacency matrix", fontsize=13)

    indices = np.arange(len(vec_min))

    # Smallest eigenvalue eigenvector
    ax1.bar(indices, vec_min, color='steelblue', width=1.0, edgecolor='none')
    ax1.set_xlabel("Component index", fontsize=12)
    ax1.set_ylabel("Amplitude", fontsize=12)
    ax1.set_title(rf"Smallest eigenvalue $\lambda = {val_min:.2f}$", fontsize=12)
    ax1.grid(True, alpha=0.3, axis='y')

    # Largest eigenvalue eigenvector
    ax2.bar(indices, vec_max, color='indianred', width=1.0, edgecolor='none')
    ax2.set_xlabel("Component index", fontsize=12)
    ax2.set_ylabel("Amplitude", fontsize=12)
    ax2.set_title(rf"Largest eigenvalue $\lambda = {val_max:.2f}$", fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.show()


# -------------------------------------------


if __name__ == "__main__":

    SetTex()

    # Verify: 10 smallest eigenvalues of 8D cube
    eigs_8d = smallest_eigenvalues(8, k=10)
    print("10 smallest eigenvalues of 8D hypercube:")
    print(np.round(eigs_8d).astype(int))

    # Timing up to 22 dimensions
    dims, times = measure_generation_times(max_dim=22)
    plot_timing(dims, times)

    # Eigenvectors of 6D cube
    plot_eigenvectors(N=6)
