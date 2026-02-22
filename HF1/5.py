import matplotlib.pyplot as plt
import matplotlib as mpl


class EulerIntegrator:
    """Encapsulates the Euler integration with different modes"""

    dt: float
    N: int
    t_data: list
    x_data: list
    y_data: list
    rabs_data: list
    E_data: list

    def __init__(self, dt, N, r0=(1, 0), v0=(0, 1)):
        """
        It defines all the values used class-wise, and creates all the data lists.
        :param dt: Delta t, time.
        :param N: Number of iterations
        :param r0: The initial position
        :param v0: The initial velocity
        """

        self.dt = dt
        self.N = int(N)
        self.r0 = r0
        self.v0 = v0

        # Set data
        self.t_data = []
        self.x_data = []
        self.y_data = []
        self.rabs_data = []
        self.E_data = []

    def SetInitVars(self):
        """
        This function sets the initial values.
        :return: All initial values, calculated or given.
        """

        # Set t0
        t0 = 0

        # Set r0
        x = self.r0[0]
        y = self.r0[1]

        # Set v0
        vx = self.v0[0]
        vy = self.v0[1]

        # Calculate a0
        r_abs = (x**2 + y**2)**(1/2)
        ax = - x / r_abs**3
        ay = - y / r_abs**3

        # Calculate E0
        E = 0.5 * (vx ** 2 + vy ** 2) - 1 / r_abs

        # Fill initial values
        self.x_data.append(x)
        self.y_data.append(y)
        self.rabs_data.append(r_abs)
        self.E_data.append(E)
        self.t_data.append(t0)

        return t0, x, y, vx, vy, ax, ay

    def StandardMode(self, x, y, vx, vy, ax, ay):
        """
        Updates the position and velocity in 'std', standard mode.
        :param x: x position
        :param y: y position
        :param vx: x component of v
        :param vy: y component of v
        :param ax: x component of a
        :param ay: y component of a
        :return: The recalculated values of velocity and position.
        """

        # Calc r, first
        x += vx * self.dt
        y += vy * self.dt

        # Calc v, afterward
        vx += ax * self.dt
        vy += ay * self.dt

        return x, y, vx, vy

    def FlipMode(self, x, y, vx, vy, ax, ay):
        """
        Updates the position and velocity in 'flp', flip mode.
        :param x: x position
        :param y: y position
        :param vx: x component of v
        :param vy: y component of v
        :param ax: x component of a
        :param ay: y component of a
        :return: The recalculated values of velocity and position.
        """

        # Calc v, first
        vx += ax * self.dt
        vy += ay * self.dt

        # Calc r, afterward
        x += vx * self.dt
        y += vy * self.dt

        return x, y, vx, vy

    def Core_Calculations(self, mode: bool):
        """
        This function does the core calculations.
        :param mode: Selected mode, True for 'std', False for 'flp'
        """

        t, x, y, vx, vy, ax, ay = EulerIntegrator.SetInitVars(self)

        for i in range(self.N):
            if mode:
                x, y, vx, vy = self.StandardMode(x, y, vx, vy, ax, ay)
            else:
                x, y, vx, vy = self.FlipMode(x, y, vx, vy, ax, ay)

            # Calc a
            r_abs = (x ** 2 + y ** 2) ** (1 / 2)
            ax = - x / r_abs ** 3
            ay = - y / r_abs ** 3

            # Calc E
            E = 0.5 * (vx ** 2 + vy ** 2) - 1 / r_abs

            t += self.dt

            self.t_data.append(t)
            self.x_data.append(x)
            self.y_data.append(y)
            self.rabs_data.append(r_abs)
            self.E_data.append(E)

    def main(self, mode: str):
        """
        The 'main' function initiates the calculations, by matching the 'mode' to a valid output.
        :param mode: Selected mode, 'str' for standard mode, 'flp' for flip mode.
        """

        match mode:
            case 'std':
                self.Core_Calculations(mode=True)
            case 'flp':
                self.Core_Calculations(mode=False)
            case _:
                raise ValueError(f"Undefined mode '{mode}'; expected 'std' or 'flp'.")


def euler_integrator(dt, N, mode: str = 'std'):
    """
    Calls the 'EulerIntegrator' class. The function is only a wrapper for the class in this solution of the task.
    :param dt: Delta t, time
    :param N: Number of iterations
    :param mode: Selected mode
    :return: The variables of the 'EulerIntegrator' class, arranged into a dict.
    """

    ei = EulerIntegrator(dt, N)
    ei.main(mode)

    return vars(ei)

# -------------------------------------


def SetTex():
    """
    Sets TeX fonts.
    """

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


def axis_constructor(axis, dt, N, mode, title: str, xl: str, yl: str, plot_x: str, plot_y: str, color='steelblue'):
    """
    Constructs the axes.
    :param axis: Current axis
    :param dt: Delta t, time.
    :param N: Number of iterations
    :param mode: Selected mode
    :param title: Title
    :param xl: x label
    :param yl: y label
    :param plot_x: x-axis of plot
    :param plot_y: y-axis of plot
    :param color: Line color
    """

    axis.set_box_aspect()

    axis.set_title(title, fontsize=13)
    axis.set_xlabel(xl, fontsize=15)
    axis.set_ylabel(yl, fontsize=15)

    results = euler_integrator(dt, N, mode)
    axis.plot(results[plot_x], results[plot_y], '-', color=color)


def plot(dt, mode, size=(8, 8)):
    """
    Main plotting function, plots everything.
    :param dt: Delta t, time
    :param mode: Selected mode
    :param size: Size of the figure
    """

    SetTex()

    fig = plt.figure(figsize=size)

    gs = fig.add_gridspec(2, 2)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])

    n = round(100/dt)

    axis_constructor(ax1, dt, n, mode,
                     "The Trajectory.", 'x', 'y',
                     'x_data', 'y_data', 'steelblue')

    axis_constructor(ax2, dt, n, mode,
                     "The Energy of the orbit over time.", 't', 'E',
                     't_data', 'E_data', 'crimson')

    axis_constructor(ax3, dt, n, mode,
                     "The radius over time.", 't', 'r',
                     't_data', 'rabs_data', 'navy')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot(0.1, "flp")
