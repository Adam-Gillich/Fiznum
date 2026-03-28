import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy

# ----------------------------------
# File location
# ----------------------------------

file = 'CNTs.data.npy'


# ----------------------------------
# Requested functions
# ----------------------------------


def get_orientation_and_tilt(r0) -> tuple:
    tube = r0

    r_n = PositionToCenter(tube)

    I = MomentOfInertia(r_n)

    # Solve for Hermitian
    if scipy.linalg.ishermitian(I):
        val, vec = scipy.linalg.eigh(I, subset_by_index=[0, 0])
        orientation = vec[:, 0]
    else:
        # if not Hermitian, fall back to general
        vals, vecs = scipy.linalg.eig(I)
        index = np.argmin(vals.real)
        orientation = vecs[:, index].real

    if orientation[0] < 0:
        orientation = -orientation

    # Tilt angle in the x-z plane (y \approx 0 for all tubes)
    tilt = np.atan2(orientation[0], orientation[2])

    return orientation, tilt


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


def read_npy(filename: str) -> list:
    """

    :param filename: File location
    :return:
    """

    raw_data = np.load(filename, allow_pickle=False)
    shape = raw_data.shape

    data = []

    for i in range(0, shape[1], 3):
        x = [k for k in raw_data[:, i + 0]]
        y = [k for k in raw_data[:, i + 1]]
        z = [k for k in raw_data[:, i + 2]]

        data.append(np.array(list(zip(x, y, z))))

    return data


def CenterMass(tube) -> np.ndarray:
    return np.mean(tube, axis=0)


def PositionToCenter(tube) -> np.ndarray:
    R = CenterMass(tube)
    r_n = tube - R
    return r_n


def MomentOfInertia(tube) -> np.ndarray:
    r_dot_r = np.einsum('ni,ni->n', tube, tube)

    left = np.sum(r_dot_r) * np.eye(3)
    right = np.einsum('ni,nj->ij', tube, tube)

    return left - right


def ShiftToZero(tube) -> np.ndarray:
    """
    Shifts the coordinates of a tube so that its center of mass is at (0, 0, 0).
    """
    return tube - CenterMass(tube)

# ----------------------------------
# Plot
# ----------------------------------


class Plot:

    def __init__(self, tubes):
        self.tubes = tubes

        SetTex()

    def xy_xz_yz(self, annotate=False):

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 6))

        # Plot nanotubes
        settings2 = [(ax1, 0, 1), (ax2,  0, 2), (ax3, 1, 2)]

        # ----------------------------------------------------------------
        # Just for convenience if I have to find a nanotube.
        if annotate:
            for i, tube in enumerate(self.tubes):
                R = CenterMass(tube)
                for ax, x, y in settings2:
                    ax.plot(tube[:, x], tube[:, y])
                    ax.text(R[x], R[y], str(i))
        # ----------------------------------------------------------------
        else:
            # Real needed stuff
            for tube in self.tubes:
                for ax, x, y in settings2:
                    ax.plot(tube[:, x], tube[:, y])

        # Plot the labels and stuff
        fig.suptitle(r'\textsc{The nanotubes from different angles}', fontsize=20)

        settings = [(ax1, ['z', 'x', 'y']),  (ax2, ['y', 'x', 'z']), (ax3, ['x', 'y', 'z'])]
        lim = 850

        for ax, names in settings:
            ax.set_title(fr'\textbf {'{'} The nanotubes from {names[0]}-axis {'}'}', fontsize=14)
            ax.set_xlabel(f'{names[1]}', fontsize=16)
            ax.set_ylabel(f'{names[2]}', fontsize=16)
            ax.set_xlim(-lim, lim)
            ax.set_ylim(-lim, lim)
            ax.set_aspect('equal')

        plt.tight_layout()
        plt.show()

    def three_tubes(self, chosen_nanotubes: list, Limited=False, lim: int = None):

        fig, ax = plt.subplots(1, 1, figsize=(7, 7))

        # Plot the chosen nanotubes
        settings = chosen_nanotubes

        for index in settings:
            tube_shifted = ShiftToZero(self.tubes[index])
            vec, tilt = get_orientation_and_tilt(self.tubes[index])

            # Plot the tube
            plt.plot(tube_shifted[:, 0], tube_shifted[:, 2])
            shift_out = 95
            plt.text(vec[0] * shift_out, vec[2] * shift_out, str(index))

            # Plot vector
            origin = np.array([0, 0])
            plt.quiver(*origin, vec[0], vec[2], scale=4, color='k', width=0.01, zorder=10)

        # ----------------------------------------------------------------
        # For your attention this below is completely and utterly redundant
        # I just felt like it, move on.
        if Limited and lim is not None:
            ax.set_xlim(-lim, lim)
            ax.set_ylim(-lim, lim)
        elif Limited and lim is None:
            raise ValueError("'lim' is missing. The plot cannot be limited.")
        elif not Limited and lim is not None:
            import warnings
            warnings.warn("'Limited' is still False. The limit won't be applied to the plot.")
        # ----------------------------------------------------------------

        # Plot labels
        ax.set_title(fr'\textbf {'{'} The chosen nanotubes and their vectors, {settings} {'}'}', fontsize=14)
        ax.set_xlabel('x', fontsize=16)
        ax.set_ylabel('z', fontsize=16)

        ax.set_aspect('equal')
        plt.show()

    def tilt_vs_index(self):

        plt.figure(figsize=(8, 6))

        tilts = [get_orientation_and_tilt(i)[1] for i in self.tubes]
        mean = float(np.mean(tilts))

        plt.axhline(mean, c='r', label=f'Mean = {mean}')

        for index, tilt in enumerate(tilts):
            plt.bar(index, tilt)

        plt.title(r'\textbf{The tilt as a function of the index}', fontsize=16)
        plt.xlabel(r'\textsc{index}', fontsize=14)
        plt.ylabel(r'\textsc{tilt} [$rad$]', fontsize=14)

        plt.legend()
        plt.show()


if __name__ == '__main__':
    tubes = read_npy(file)

    plot = Plot(tubes)

    plot.xy_xz_yz()

    plot.three_tubes([0, 13, 43])

    plot.tilt_vs_index()
