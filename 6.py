import matplotlib.pyplot as plt
import numpy as np


class Graf19:
    """
    This class creates a hexagonal graph with 19 points.
    """

    def __init__(self):
        """
        Initiates the class, by setting up the requested starting state, and creating the class variables.
        """
        self.A = []
        self.coords = []
        self.coords_dict = {}

        self.MakeHex()
        self.MakeAdjMatrix()
        self.InitDisconnect()

    # ------------------------------------------------
    # Execute inside
    # ------------------------------------------------

    def MakeHex(self, radius=2):
        """
        This function makes the hexagonal grid.
        :param radius: Controls how big the grid will be.
        """

        # Base vectors
        er = np.array([0, 1])
        eq = np.array([np.cos(np.pi / 6), 0.5])

        for q in range(-radius, radius + 1):
            for r in range(-radius, radius + 1):
                # The requirement for hex geometry: q, r, s <= radius, we had q, r done already
                s = -q - r
                # Without this check we get a sheered grid of points.
                if abs(s) <= radius:
                    p = q * eq + r * er
                    self.coords.append(p)

        self.MakeCordsDict()

    def MakeCordsDict(self):
        """
        For easier access, converts 'coords' into a dict where the keys are the string indexes of 'coords'.
        """

        for i, n in enumerate(self.coords):
            self.coords_dict.update({str(i): n})

    def MakeAdjMatrix(self, tol=1e-6):
        """
        This function makes the Adjacency Matrix for the grid.
        :param tol: Tolerance
        :return: Adjacency Matrix
        """

        # Make an empty n*n matrix
        n = len(self.coords)
        self.A = np.zeros((n, n))

        for i, n in enumerate(self.coords):
            for j, m in enumerate(self.coords):
                # Basic idea is: Connect the points that are 1 unit apart.
                dis = np.linalg.norm(n - m)
                if abs(dis - 1) < tol:
                    self.A[i, j] = 1
                    self.A[j, i] = 1

        return self.A

    def InitDisconnect(self):
        """
        This function manually removes any unwanted connections. To achieve the requested initial state.
        """

        neighbours = self.GetNeighbours('9')

        for i in neighbours:
            if i == '5' or i == '8' or i == '14':
                self.A[9][int(i)] = 0
                self.A[int(i)][9] = 0

        self.A[8][7] = 0
        self.A[4][3] = 0
        self.A[13][12] = 0
        self.A[13][17] = 0
        self.A[14][18] = 0
        self.A[10][15] = 0
        self.A[6][10] = 0
        self.A[2][5] = 0
        self.A[1][4] = 0

        # ----------------------

        self.A[7][8] = 0
        self.A[3][4] = 0
        self.A[12][13] = 0
        self.A[17][13] = 0
        self.A[18][14] = 0
        self.A[15][10] = 0
        self.A[10][6] = 0
        self.A[5][2] = 0
        self.A[4][1] = 0

    # ------------------------------------------------
    # Helpers
    # ------------------------------------------------

    def GetNeighbours(self, index: str, tol=1e-6):
        """
        Obtains the neighbouring points of a given point.
        :param index: Given index of a point.
        :param tol: Tolerance
        :return: Dictionary, where keys are the indexes and the values are the point coordinates.
        """

        # To index the dict["key"] must be passed.
        center = self.coords_dict[index]
        neighbours = {}

        # Basic idea is: Get the points that are 1 unit from our point given by 'index'.
        for i in self.coords_dict:
            dis = np.linalg.norm(center - self.coords_dict[i])
            if abs(dis - 1) < tol:
                neighbours.update({str(i): self.coords_dict[i]})

        return neighbours

    def TheBig7(self):
        """
        "TheBig7" are the middle seven points in the grid: vertex '9' and its 6 neighbours.
        They must be known for the red-point checks and flip conditions.
        :return: Dictionary, where keys are the indexes and the values are the point coordinates.
        """

        thebig7 = {'9': [0, 0]}

        thebig7.update(self.GetNeighbours('9'))
        return thebig7

    def Flip(self, index):
        """
        This function flips the values of the Adjacency Matrix, around a given point.
        Thus, all connections will be flipped.
        :param index: Given index of a point
        """

        neighbours = self.GetNeighbours(index)

        for i in neighbours:
            if self.A[int(index)][int(i)] == 1:
                self.A[int(index)][int(i)] = 0
                self.A[int(i)][int(index)] = 0
            else:
                self.A[int(index)][int(i)] = 1
                self.A[int(i)][int(index)] = 1

    def ThreeConnection(self, index):
        """
        Checks whether a given point of "TheBig7" has exactly three connections, hence it is flippable.
        :param index: Given index of a point.
        :return: If True then the point can be flipped.
        """

        connections = 0

        for n in self.A[int(index)]:
            connections += n

        if connections == 3:
            return True
        else:
            return False

    # ------------------------------------------------
    # Plot functions
    # ------------------------------------------------

    # --------------------
    # Execute during plot
    # --------------------

    def CheckRed(self):
        """
        This function checks which points ought to be turned red. The condition is having exactly three connections.
        :return: The coordinates of the points to be marked red, and their indexes, for the title of the plots.
        """

        connections = 0
        markred = []
        indexes = []

        for i in self.TheBig7():
            for n in self.A[int(i)]:
                connections += n

            if connections == 3:
                markred.append(self.TheBig7()[i])
                indexes.append(str(i))
                connections = 0
            else:
                connections = 0

        return np.array(markred), indexes

    def Connect(self, axis):
        """
        This function connects the points according to the Adjacency Matrix.
        :param axis: Current axis
        """

        n = len(self.coords)

        for i in range(n):
            for j in range(i + 1, n):
                if self.A[i][j] == 1:
                    x = [self.coords[i][0], self.coords[j][0]]
                    y = [self.coords[i][1], self.coords[j][1]]
                    axis.plot(x, y, 'k')

    @staticmethod
    def initials(axis):
        """
        Removes everything unnecessary for the plots.
        :param axis: Current axis.
        """

        axis.set_aspect('equal')

        axis.spines['top'].set_visible(False)
        axis.spines['bottom'].set_visible(False)
        axis.spines['left'].set_visible(False)
        axis.spines['right'].set_visible(False)
        axis.set_xticks([])
        axis.set_yticks([])

    # ------------------------------------------------
    # Execute outside
    # ------------------------------------------------

    def megfordit(self, csucs_index: str):
        """
        This function checks whether a point satisfies the conditions to be flipped, then calls the 'Flip' function.
        :param csucs_index: Given index of a point.
        :return: Flip the connections if everything is satisfied. If the given point isn't part of "TheBig7" then a 'str', and if the given point of "TheBig7" doesn't have three connections, then nothing.
        """

        if csucs_index in self.TheBig7().keys():
            if self.ThreeConnection(csucs_index):
                self.Flip(csucs_index)
            else:
                pass
        else:
            return "Nem belső csúcsot adtál meg, ezért nem csinálok semmit!"

    def rajzol(self, axis):
        """
        This plots the current state of the graph.
        :param axis: Current axis
        """

        self.Connect(axis)

        # -------- Plot --------
        self.initials(axis)

        # To turn the hex from tie-fighter to JWST is to plot (y, -x) instead of (x, y)
        points = np.array(self.coords)
        axis.plot(points[:, 0], points[:, 1], "o", markeredgewidth=0.8,
                  markerfacecolor='white', markeredgecolor='k', markersize=9)

        reds, title = self.CheckRed()
        axis.plot(reds[:, 0], reds[:, 1], "ro", markeredgewidth=0.8, markeredgecolor='k', markersize=9)

        axis.set_title(title)


# -------------------------------------------------------------------------


def main():
    """
    Creates a Graf19 instance, then plots three states of the graph:
    the initial state, after flipping point '9', and after flipping point '10'.
    """

    hexa = Graf19()

    fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(12, 4))

    hexa.rajzol(ax1)

    hexa.megfordit('9')
    hexa.rajzol(ax2)

    hexa.megfordit('10')
    hexa.rajzol(ax3)

    plt.show()


if __name__ == "__main__":
    main()
