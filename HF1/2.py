import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as wid


def myinv(A):
    """
    Creates a 2x2 matrix inverse.
    :param A: An array.
    :return: Inverse array.
    """

    inv = (1 / (A[0][1] * A[1][1] - A[0][1] * A[1][0])) * np.array([[A[1][1], -A[0][1]],
                                                                    [-A[1][0], A[0][0]]])
    return inv


def rot(phi):
    """
    Creates rotation matrix.
    :param phi: Given degree.
    :return: Rotation array.
    """

    return np.array([[np.cos(phi), -np.sin(phi)],
                     [np.sin(phi), np.cos(phi)]])


# ----------------------------------

def TrueGenGrid(base, n, i, j, coords):
    """
    This creates the coordinates of the grid, recursively.
    :param base: Base matrix.
    :param n: Max coulomb.
    :param i: Position index parameter. (x)
    :param j: Position index parameter. (y)
    :param coords: List of coordinates. It must be passed through for the function to work properly.
    :return: The coordinates of the grid, in a list.
    """

    if i == n:
        return coords

    vec = np.array([i, j])

    coords.append(base @ vec)
    j += 1
    if j == n:
        i += 1
        j = 0
        return TrueGenGrid(base, n, i, j, coords)
    return TrueGenGrid(base, n, i, j, coords)


def gen_grid(phi, N):
    """
    This function satisfies the initial parameter requirements, to construct the grid.
    :param phi: Degree by which we want to turn the grid.
    :param N: Whole number, that defines the size of the bars.
    :return: The coordinates of the grid, in a list.
    """

    B = np.array([[1, 0],
                  [0, 1]])
    base = rot(phi) @ B
    n = 2 * N + 1
    grid = TrueGenGrid(base, n, 0, 0, [])

    return grid


# ---------------------------------

def gen_mvec(phi):
    """
    This function creates the moivre vectors.
    :param phi: Degree by which the vectors must be turned.
    :return: A matrix.
    """

    G1 = 2 * np.pi * np.array([1, 0])
    G2 = 2 * np.pi * np.array([0, 1])

    g1 = G1 - G1 @ rot(phi).T
    g2 = G2 - G2 @ rot(phi).T

    M = 2 * np.pi * myinv(
        np.array([[g1[0], g1[1]],
                  [g2[0], g2[1]]])
    )
    return M


# --------------------------------

def plot(N, phi):
    """
    This function plots the graph of the grids and vectors.
    :param N: Size parameter.
    :param phi: Degree by which the grid is turned.
    :return: Plots teh graph.
    """

    points = np.array(gen_grid(phi, N))
    stockgrid = np.array(gen_grid(0, N))

    M = gen_mvec(phi)
    mV = np.array([[M[0][0], M[1][0]], [M[0][1], M[1][1]]])
    origin = np.array([[-30, -30], [10, 10]])
    plt.quiver(*origin, mV[:, 0], mV[:, 1], color=['r', 'b'], scale=50)

    plt.gca().set_aspect('equal')

    plt.plot(points[:, 0], points[:, 1], '-')
    plt.plot(stockgrid[:, 0], stockgrid[:, 1], 'r-')
    plt.show()


if __name__ == "__main__":
    # print(gen_mvec(0.02))
    # print(gen_grid(0, 3))
    # plot(26, np.pi / 4)
    wid.interact(plot, N=(1, 26, 1), phi=(0.01, np.pi/6, 0.0025))