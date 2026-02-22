import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as wid


def myinv(A):
    """
    Creates a 2x2 matrix inverse.
    :param A: A matrix, 2x2 numpy array.
    :return: Inverse matrix.
    """

    inv = (1 / (A[0][0] * A[1][1] - A[0][1] * A[1][0])) * np.array([[A[1][1], -A[0][1]],
                                                                    [-A[1][0], A[0][0]]])
    return inv


def rot(phi):
    """
    Creates rotation matrix.
    :param phi: Given angle.
    :return: Rotation matrix.
    """

    return np.array([[np.cos(phi), -np.sin(phi)],
                     [np.sin(phi), np.cos(phi)]])


# ----------------------------------

def TrueGenGrid(base, begin, end, i, j, coords):
    """
    This creates the coordinates of the grid, recursively. Begin and end are needed to check,
    and reset the counters, i and j, which aren't constants, but are always changing.
    :param base: Base matrix.
    :param begin: Begin index
    :param end: End index.
    :param i: Current row index.
    :param j: Current column index.
    :param coords: List of coordinates. It accumulates with each iteration.
    :return: The coordinates, 'coords', of the grid, in a numpy array.
    """

    if i == end:
        return np.array(coords)

    vec = np.array([i, j])

    coords.append(base @ vec)
    j += 1
    if j == end:
        i += 1
        j = begin
        return TrueGenGrid(base, begin, end, i, j, coords)

    return TrueGenGrid(base, begin, end, i, j, coords)


def gen_grid(phi, N):
    """
    This function satisfies the initial parameter requirements, to construct the grid.
    :param phi: Angle by which we want to turn the grid.
    :param N: Whole number, that defines the size of the grid.
    :return: The coordinates of the grid, in a numpy array.
    """

    B = np.array([[1, 0],
                  [0, 1]])
    base = rot(phi) @ B
    n = 2 * N + 1
    grid = TrueGenGrid(base, -N, N+1, -N, -N, [])

    return grid


def Connect(coords, N, lcolor):
    """
    This function makes the points connect,
    so that the end point of a column doesn't connected to the next column's first point.
    :param coords: List of coordinates.
    :param N: Whole number, that defines the size of the grid.
    :param lcolor: Line color.
    """
    n = 2 * N + 1

    def draw_if_vertical(k):
        if k % n != n - 1:
            plt.plot([coords[k][0], coords[k+1][0]],
                     [coords[k][1], coords[k+1][1]], '-', color=lcolor)

    list(map(draw_if_vertical, range(len(coords))))


# ---------------------------------

def gen_mvec(phi):
    """
    This function creates the moiré vectors.
    :param phi: Angle by which the vectors must be turned.
    :return: A matrix, containing the moiré vectors.
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

def plot(N, phi, lines=True):
    """
    This function plots the graph of the grids and vectors.
    :param N: Size parameter.
    :param phi: Degree by which the grid is turned.
    :param lines: A mode parameter, if True, the resulting plot will have lines. Otherwise, points.
    """

    fig, ax = plt.subplots()

    # Set plot
    ax.set_aspect('equal')
    fig.set_size_inches(5, 5)

    # Make grids
    stockgrid = gen_grid(0, N)
    rotgrid = gen_grid(phi, N)

    # Make vectors
    M = gen_mvec(phi)
    mV = np.array([[M[0][0], M[1][0]], [M[0][1], M[1][1]]])
    origin = np.array([[0, 0], [0, 0]])
    plt.quiver(*origin, M[:, 0], M[:, 1], color=['k', 'k'], scale=50)

    # Check mode
    if lines:
        Connect(rotgrid, N, lcolor='red')
        Connect(stockgrid, N, lcolor='blue')
    else:
        plt.plot(rotgrid[:, 0], rotgrid[:, 1], 'ro')
        plt.plot(stockgrid[:, 0], stockgrid[:, 1], 'bo')

    plt.show()


if __name__ == "__main__":

    plot(3, np.pi/24)

    # wid.interact(plot, N=(1, 6, 1), phi=(0.01, np.pi/6, 0.0025))
