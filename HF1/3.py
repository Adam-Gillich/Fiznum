import matplotlib.patches
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

fig, (ax1, axint, ax2) = plt.subplots(nrows=1, ncols=3, gridspec_kw={"width_ratios": [4, 1.5, 4]})
pi = np.pi


# -----------------------------------------------------------


def MakeLine(axis, begin, end, **attributes):
    """
    Makes a line between two points.
    :param axis: Current axis.
    :param begin: Beginning point
    :param end: End point.
    :param attributes: Extra attributes for 'axis.plot()'.
    :return: Plots a line.
    """

    x = np.array([begin[0], end[0]])
    y = np.array([begin[1], end[1]])

    axis.plot(x, y, **attributes)


def MakeCircleToXY(radius, phi, center=(0, 0)):
    """
    Converts the coordinates of a point of a circle to x and y values.
    :param radius: Radius of the circle.
    :param phi: Phase angle of the circle.
    :param center: Center of the circle.
    :return: Coordinates in a tuple.
    """

    xc, yc = center
    theta = np.deg2rad(phi)

    x = xc + radius * np.cos(theta)
    y = yc + radius * np.sin(theta)

    coord = (x, y)

    return coord


def MakeProgressArc(axis, radius, begin, end, n, color, center=(0, 0)):
    """
    Makes the required curve with the color progressing points.
    :param axis: Current axis.
    :param radius: Radius of the circle.
    :param begin: Beginning angle.
    :param end: Ending angle.
    :param n: Number of points.
    :param color: Color of the line below the points.
    :param center: Center of the circle.
    :return: Plots the points and line.
    """

    xc, yc = center

    # Make Arc     ------------------------------------
    phi = np.linspace(np.deg2rad(begin),
                      np.deg2rad(end), 100)

    x = xc + radius * np.cos(phi)
    y = yc + radius * np.sin(phi)

    axis.plot(x, y, color=color, linewidth=1)

    # Make Points ------------------------------------
    points = np.linspace(np.deg2rad(begin),
                         np.deg2rad(end), n)

    xp = xc + radius * np.cos(points)
    yp = yc + radius * np.sin(points)

    # Color Map
    cmap = mpl.colors.LinearSegmentedColormap.from_list('white_blue',
                                                        ['white', 'midnightblue'])

    for i in range(n):
        icolor = i / (n - 1)

        axis.plot(xp[i], yp[i], 'o', markersize=4, markeredgewidth=0.8,
                  markerfacecolor=cmap(icolor), markeredgecolor=color)


def MakeArcArrow(axis, radius, begin, end, color, center=(0, 0)):
    """
    Makes the required arrow arcs.
    :param axis: Current axis.
    :param radius: Radius of the circle.
    :param begin: Beginning angle.
    :param end: Ending angle.
    :param color: Color of the line and arrow.
    :param center: Center of the circle.
    :return: Plots the required arrow arc.
    """

    xc, yc = center

    # Make linspace
    phi = np.linspace(np.deg2rad(begin),
                      np.deg2rad(end), 100)

    x = xc + radius * np.cos(phi)
    y = yc + radius * np.sin(phi)

    axis.plot(x, y, color=color, linewidth=1)

    # Arrow direction
    dx = -np.sin(phi[-1])
    dy = np.cos(phi[-1])

    head_width = 0.5
    axis.arrow(
        x[-1], y[-1],
        dx * 0.2, dy * 0.2,
        head_width=head_width,
        head_length=2.5 * head_width,
        length_includes_head=False,
        edgecolor=color, facecolor=color, fill=True
    )

# -----------------------------------------------------------
# For axint
# -----------------------------------------------------------


def axintMakeArcArrow(axis, radius, begin, end, color, center=(0, 0)):
    """
    Makes the required arrow arc for the intermediate subplot.
    :param axis: Current axis.
    :param radius: Radius of the circle.
    :param begin: Beginning angle.
    :param end: Ending angle.
    :param color: Color of the line and arrow.
    :param center: Center of the circle.
    :return: Plots the required arrow arc.
    """

    xc, yc = center

    # Make linspace
    phi = np.linspace(np.deg2rad(begin),
                      np.deg2rad(end), 100)

    x = xc + radius * np.cos(phi)
    y = yc + radius * np.sin(phi)

    axis.plot(x, y, color=color, linewidth=1)

    # Arrow direction
    dx = np.sin(phi[-1])
    dy = -np.cos(phi[-1])

    head_width = 0.8
    axis.arrow(
        x[-1], y[-1],
        dx * 0.2, dy * 0.2,
        head_width=head_width,
        head_length=2.5 * head_width,
        length_includes_head=False,
        edgecolor=color, facecolor=color, fill=True
    )


# -----------------------------------------------------------


def initials(axis):
    """
    This function creates the common elements between the plots.
    :param axis: Chosen axis to plot on.
    :return: Bunch of stuff to plot.
    """

    axis.set_aspect('equal')
    plt.gcf().set_size_inches(10, 5 - 1.12)

    # Remove everything, basically.
    axis.spines['top'].set_visible(False)
    axis.spines['bottom'].set_visible(False)
    axis.spines['left'].set_visible(False)
    axis.spines['right'].set_visible(False)
    axis.set_xticks([])
    axis.set_yticks([])

    # Origin
    origin = np.array([0, 0])

    # Set x, y limits
    axis.set_xlim(-10.1, 10.1)
    axis.set_ylim(-10.1, 10.1)

    # Make x, y lines
    line_attributes = dict(color='darkslateblue', linestyle='-', lw=1)
    axis.axhline(y=0, **line_attributes)
    axis.axvline(x=0, **line_attributes)

    # Set origin, point and 0.
    origin_attributes = dict(marker='o',
                             markerfacecolor='white',
                             markeredgecolor='darkslateblue',
                             markersize=3
                             )
    axis.plot(origin[0], origin[1], **origin_attributes)

    # Set origin text
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'
    axis.text(0.3, -1.2, r"0", fontsize=11)


def texts():
    """
    Plots all the texts of all the plots.
    :return: Text plots.
    """

    # Axis 1 texts
    ax1.text(-10, 10, r"$z$-plane", fontsize=15)
    ax1.text(-9.3, -1.2, r"\textbf{-1}", fontsize=12)
    ax1.text(8.5, -1.2, r"\textbf{1}", fontsize=12)

    ax1.text(0.3, 8.5, r"\textbf{i}", fontsize=12)
    ax1.plot(0, 8, marker='o',
             markerfacecolor='white',
             markeredgecolor='darkslateblue',
             markersize=3
             )

    # Axis 2 texts
    ax2.text(-10, 10, r'$w$-plane', fontsize=15)
    ax2.text(-9.3, -1.2, r"\textbf{-1}", fontsize=12)
    ax2.text(8.5, -1.2, r"$\mathbf{1} = \sqrt[\mathbf{3}]{\mathbf{1}}$", fontsize=12)

    x, y = MakeCircleToXY(8, 90+30)
    ax2.plot(x, -y, marker='o',
             markerfacecolor='white',
             markeredgecolor='darkslateblue',
             markersize=3
             )
    ax2.text(x-2.3, y+0.3, r"$\sqrt[\mathbf{3}]{\mathbf{1}}$", fontsize=12)
    ax2.text(x-2.3, -(y+1), r"$\sqrt[\mathbf{3}]{\mathbf{1}}$", fontsize=12)

    # Intermediate Axis text
    axint.text(-2, 4, r"$w = \sqrt[\mathbf{3}]{z}$", fontsize=12)


def axis1():
    """
    This plots everything for 'ax1'.
    :return: Plots various things.
    """

    # Patches
    outer = ax1.add_patch(plt.Circle((0, 0), 10, color='lightsteelblue'))
    inner = ax1.add_patch(plt.Circle((0, 0), 2, color='white'))

    initials(ax1)

    MakeArcArrow(ax1, 6, 45, 180 + 30, 'darkslateblue')
    MakeProgressArc(ax1, 8, 1.5, 358.5, 19, 'darkslateblue')


def axis2():
    """
    This plots everything for 'ax2'.
    :return: Plots various things.
    """

    # Patches
    outer = ax2.add_patch(mpl.patches.Wedge((0, 0), 8.5, 0, 90 + 30,
                                            color='lightsteelblue'))
    inner = ax2.add_patch(mpl.patches.Wedge((0, 0), 5.5, 359, 90 + 31,
                                            color='white'))
    x1, y1 = MakeCircleToXY(8, 90 + 30)
    x2, y2 = MakeCircleToXY(8, 180 + 60)
    MakeLine(ax2, (0, 0), (x1, y1), color='darkslateblue', lw=1)
    MakeLine(ax2, (0, 0), (x2, y2), color='darkslateblue', lw=1)

    initials(ax2)

    circle = ax2.add_patch(plt.Circle((0, 0), 8, fill=False, color='darkslateblue', linewidth=1))
    MakeProgressArc(ax2, 8, 0, 90 + 30, 19, 'darkslateblue')
    MakeArcArrow(ax2, 6.5, 40, 90, 'darkslateblue')


def axis_int():
    """
    This plots everything for 'axint'.
    :return: Plots various things.
    """

    axint.set_aspect('equal')
    axint.set_xlim(-3, 5)
    axint.set_ylim(-3, 5)

    axint.spines['top'].set_visible(False)
    axint.spines['bottom'].set_visible(False)
    axint.spines['left'].set_visible(False)
    axint.spines['right'].set_visible(False)
    axint.set_xticks([])
    axint.set_yticks([])

    axintMakeArcArrow(axint, 15, 90+10, 90-6, 'black', (0, -12))

# -----------------------------------------------------------


def plot():
    """
    The main plot function. Ultimately this creates the image.
    :return: Plots.
    """

    axis1()
    axis2()
    axis_int()

    texts()

    plt.show()


if __name__ == "__main__":
    plot()
