import matplotlib.patches
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

fig, (ax1, axint, ax2) = plt.subplots(nrows=1, ncols=3, gridspec_kw={"width_ratios": [4, 1.5, 4]})
pi = np.pi


# -----------------------------------------------------------


def MakeLine(axis, begin: tuple, end: tuple, **attributes):
    """
    Makes a line between two points.
    :param axis: Current axis.
    :param begin: Beginning point
    :param end: End point.
    :param attributes: Extra attributes for 'axis.plot()'.
    """

    x = np.array([begin[0], end[0]])
    y = np.array([begin[1], end[1]])

    axis.plot(x, y, **attributes)


def MakeCircleToXY(radius, phi, center=(0, 0)):
    """
    Converts the coordinates of a point of a circle to x and y values.
    :param radius: Radius of the circle.
    :param phi: Phase angle of the circle, in degrees.
    :param center: Center of the circle.
    :return: The converted coordinates in a tuple.
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
    :param begin: Beginning angle, in degrees.
    :param end: Ending angle, in degrees.
    :param n: Number of evenly spaced points.
    :param color: Color of the line below the points.
    :param center: Center of the circle.
    """

    xc, yc = center

    # Make Arc     ----------------------------------------------------------------------------------------

    # A linspace úgy működik, hogy megadsz neki két számot, hol kezdjen és hol végezzen.
    # Mivel én fokkal kezdtem el dolgozni ezért azt át kell alakítani rad-ba.
    # A harmadik paraméter '100', azt mondja meg hogy ezt az intervallumot hány részre ossza a linspace
    phi = np.linspace(np.deg2rad(begin),
                      np.deg2rad(end), 100)

    # De ez így kevés, hiszen ez még nem koordináta, csak egy szám
    # Ezért átalakítjuk a sugarat és szöget felhasználva a polár koordinátákat, x és y koordinátákká 
    # xc és yc a center x és y koordinátája, ami alapértelmezetten (ha meghívásnál egyérelműen nem adod meg, hogy
    # például center=(2, 4), akkor automatikusan mindkettő xc, és yc is 0 lesz.)
    x = xc + radius * np.cos(phi)
    y = yc + radius * np.sin(phi)

    # Majd ezt plotoljuk.
    # (a color-t a függvény meghívásánál adjuk meg)
    axis.plot(x, y, color=color, linewidth=1)

    # Make Points ----------------------------------------------------------------------------------------

    # Oké most van egy kötívünk, de nincs rajta pont
    # Fontos, hogy a pontokat az ív után plotoljuk, mert úgy kerül a tetejáre
    #
    # A linspace ugyanúgy működik, de itt at n a pontok száma
    # Tehát ha  n = 19 (mert tényleg annyi ponunk lesz), amit a függvény meghívásánál adunk meg
    # akkor a linspace-t 19 pontra fogja osztani 
    points = np.linspace(np.deg2rad(begin),
                         np.deg2rad(end), n)


    # És természetesen ezt is át kell alakítani x és y koordinátává
    xp = xc + radius * np.cos(points)
    yp = yc + radius * np.sin(points)

    # Color Map

    # Na de, hogy is legyen ez mind beszínezve?
    # A matplolib-nek (fontos, mert nem a matplolib.pyplot-nak)
    # Van egy ilyen függvénye, ami alul látható
    # A 'white_blue' a colotmap nevét definiálja (nem feltétlen szükséges, de most nemtudom hirtelen biztosra)
    # A második ['white', 'midnightblue'] pedig a range-et mondja meg
    # Tehát 'white'-tól, 'midnightblue'-ig menjen a colormap
    
    # Ezt el is nevezzük cmap-nak, mint colormap
    cmap = mpl.colors.LinearSegmentedColormap.from_list('white_blue',
                                                        ['white', 'midnightblue'])

    # És most jön a varázslat
    # A cmap, csak 0 és 1 közt tud színt rendelni egy pontunkhoz
    # Ezért az i-edik színt 0 és 1 közé kell beszorítani
    # Egy for ciklussal végig megyünk 0-tól 1-ig az icolorral, majd plotoljuk azt a pontot icolor színnel
    for i in range(n):
        # A pythonban az indexelés 0-tól indul és n-1-el végződik
        # Magyarul ha n= 19 akkor 19 pontod lesz de az intervallum 0-18-ig megy
        # ezért hogy 0-1 közt legyünk leosztunk (n-1)-el
        # pl.: 0/18, 1/18, 2/18, 3/18 . . . 18/18 
        icolor = i / (n - 1)

        # És kiplotoljuk a ponot minden alkalommal
        # Ehhez kell a pontok x és y koordinátájának (xp, és yp) i-edik eleme
        # És az 'o' modja meg hogy pontok legyenek
        # A színt pedig a markerfacecolor-nak ekll beadni
        # Ami természetesen a colormap-nek (cmap) az i-edik színe lesz (icolor)
        axis.plot(xp[i], yp[i], 'o', markersize=4, markeredgewidth=0.8,
                  markerfacecolor=cmap(icolor), markeredgecolor=color)


def MakeArcArrow(axis, radius, begin, end, color, center=(0, 0)):
    """
    Makes the required arrow arcs.
    :param axis: Current axis.
    :param radius: Radius of the circle.
    :param begin: Beginning angle, in degrees.
    :param end: Ending angle, in degrees.
    :param color: Color of the line and arrow.
    :param center: Center of the circle.
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
        edgecolor=color, facecolor=color, fill=True, overhang=0.2
    )

# -----------------------------------------------------------
# For axint
# -----------------------------------------------------------


def axintMakeArcArrow(axis, radius, begin, end, color, center=(0, 0)):
    """
    Makes the required arrow arc for the intermediate subplot.
    :param axis: Current axis.
    :param radius: Radius of the circle.
    :param begin: Beginning angle, in degrees.
    :param end: Ending angle, in degrees.
    :param color: Color of the line and arrow.
    :param center: Center of the circle.
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
        edgecolor=color, facecolor=color, fill=True, overhang=0.2
    )


# -----------------------------------------------------------


def initials(axis):
    """
    This function creates the common elements between the plots.
    Removes anything unneeded, sets the axis lines, sets the LaTeX fonts, and labels the origin.
    :param axis: Chosen axis to plot on.
    """

    axis.set_aspect('equal')
    plt.gcf().set_size_inches(10, 5 - 1.12)

    # Remove everything, unnecessary.
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
    This plots everything for 'ax1'. The patches, then initials, and the arcs and arrows.
    """

    # Patches
    outer = ax1.add_patch(plt.Circle((0, 0), 10, color='lightsteelblue'))
    inner = ax1.add_patch(plt.Circle((0, 0), 2, color='white'))

    initials(ax1)

    MakeArcArrow(ax1, 6, 45, 180 + 30, 'darkslateblue')
    MakeProgressArc(ax1, 8, 1.5, 358.5, 19, 'darkslateblue')


def axis2():
    """
    This plots everything for 'ax2'. The patches, then initials, and the arcs and arrows.
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
    This plots everything for 'axint'. Which is much less than the two other axes,
    thus removing everything unnecessary explicitly here, without a dedicated function.
    And creating the one arrow that is needed here.
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
    It combines all axis functions and the 'texts()' function.
    """

    axis1()
    axis2()
    axis_int()

    texts()

    plt.show()


if __name__ == "__main__":
    plot()
