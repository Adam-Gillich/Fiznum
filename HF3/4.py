import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import scipy as sci
import os
import matplotlib.patches as mplpat

# ----------------------------------
# File location
# ----------------------------------

directory = r'exo_data'

# ----------------------------------
# Helper functions
# ----------------------------------


class Process:
    """This class processes the directory, in multiple steps."""
    Super_data: dict[list[dict]]

    def __init__(self, dirPATH):
        self.dir = dirPATH
        self.Super_Data = {}

    @staticmethod
    def read_planet_data(filename):
        """
        This function processes individual measurement data,
        and returns the name of the star and relevant data.
        :param filename: File name
        :return: The name of the star, data dictionary where relative time and flux are the keys.
        """

        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Find star ID
        name = lines[3].split()[-1].strip('"')

        # Find keys, and fill it to a list
        keyline = lines[140]
        keys = [key.strip() for key in keyline.strip().split('|') if key.strip()]

        # Data extraction
        data_lines = lines[143:]

        # Arrange data into rows, converted into numpy array for better handling
        rows = np.array([list(map(float, line.split())) for line in data_lines])
        all_data = {key: rows[:, i] for i, key in enumerate(keys)}

        # Select only important data
        whitelist = ['RELATIVE_DATE', 'RELATIVE_FLUX_WITHOUT_SYSTEMATICS']

        data = {key: val for key, val in all_data.items() if key in whitelist}

        return name, data

    def read_dir(self):
        """
        This function reads the whole directory,
        and assigns keys to the names (star id) of
        the observed stars, and assigns a list to them,
        where each element is the output of the above
        'read_planet_data' function, and adds the file
        index to the dictionary (which is the three-digit n
        umber before the file extension), if we need to know which
        file's data we're working with. Thus creating
        the structure of Super_Data, but it is not done yet.\n
        If the structure is confusing, then I recommend you
        look at the uploaded '4_mermaid.md' file. Where a
        diagram of Super_Data's structure can be found.
        :return: "returns" semi done Super_Data
        """
        data: dict[np.ndarray and str]

        os.chdir(self.dir)
        for file in os.listdir(self.dir):
            name, data = self.read_planet_data(file)
            data.update({'file_index': file[-7:-4]})

            if name in self.Super_Data.keys():
                self.Super_Data[name].append(data)
            else:
                self.Super_Data.update({name: [data]})

    @staticmethod
    def gauss(t, c, A, sigma):
        """
        The function used for fitting, and later plotting the
        fitted parameters.\n
        Important to note, that the data is refined so the
        middle of the dip is t0=0. So we don't need t0 because
        it is 0, without exception.
        :param t: Relative time
        :param c: Background level
        :param A: Depth of the dip
        :param sigma: Width of the dip
        :return: The equation
        """

        exponent = t**2 / (2 * sigma**2)
        return c - A * np.exp(-exponent)

    def FitGaussCurves(self):
        """
        This function fits the above 'gauss' function
        to all the measurements. And adds their results
        to Super_Data. Now Super_Data is done and ready for use.
        :return: "returns" Super_Data
        """

        for key in self.Super_Data.keys():
            for i, data in enumerate(self.Super_Data[key]):
                t_data = data['RELATIVE_DATE']
                flux_data = data['RELATIVE_FLUX_WITHOUT_SYSTEMATICS']

                # c: background, middle of flux |     A: depth of curve         |        sigma: width of curve
                p0 = [np.mean(flux_data), np.mean(flux_data) - np.min(flux_data), (t_data.max() - t_data.min()) / 10]

                res, res_cov = sci.optimize.curve_fit(self.gauss, t_data, flux_data, p0=p0)

                self.Super_Data[key][i].update({'res': res})


# ----------------------------------
# Plot
# ----------------------------------

def SetTex():
    """
    Sets TeX fonts.
    """

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


class Plot:
    """This class does the plotting."""

    def __init__(self, Super_Data, graph_index=(0, 0, 0)):
        self.sup_data = Super_Data
        self.graph_index = graph_index

        SetTex()

    def flux(self):
        """
        This function plots one set of observation data,
        using the initially given 'graph_index' instance
        variable.\n
        This function is here by mistake but if
        I already wrote it why not keep it.
        """

        fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))

        fig.suptitle(r"\textbf{Relative flux as a function of relative time}", fontsize=20)

        for ax, key, index in zip(axes, self.sup_data.keys(), self.graph_index):
            data = self.sup_data[key][index]

            tdata = data['RELATIVE_DATE']
            flux_data = data['RELATIVE_FLUX_WITHOUT_SYSTEMATICS']

            ax.plot(tdata, flux_data, 'o', c='y')
            # -------------------------------------------------

            ax.set_title(fr"{key} star's flux, index: {index}", fontsize=16)
            ax.set_xlabel(r"\textsc{relative time}", fontsize=14)
            ax.set_ylabel(r"\textsc{relative flux}", fontsize=14)

            ax.set_box_aspect(1)

        plt.tight_layout()
        plt.show()

    def all_flux(self):
        """
        This function plots all sets of observation data,
        as requested.
        """

        fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))

        fig.suptitle(r"\textbf{All of the relative flux as a function of relative time}", fontsize=20)

        for ax, key in zip(axes, self.sup_data.keys()):
            star_data = self.sup_data[key]

            for data in star_data:
                tdata = data['RELATIVE_DATE']
                flux_data = data['RELATIVE_FLUX_WITHOUT_SYSTEMATICS']

                ax.plot(tdata, flux_data, '+')
                # -------------------------------------------------

                ax.set_title(fr"{key} star's flux", fontsize=16)
                ax.set_xlabel(r"\textsc{relative time}", fontsize=14)
                ax.set_ylabel(r"\textsc{relative flux}", fontsize=14)

                ax.set_box_aspect(1)

        plt.tight_layout()
        plt.show()

    def fitted_curve(self, print_res=False):
        """
        This function plots the fitted curve on
        one set of observation data. Which is
        by default all the first measurements defined by
        the 'graph_index' instance variable. By changing
        it you can choose which measurement will be plotted.\n
        By itself on the plot only the rounded
        values are shown, but if 'print_res' is True,
        then the accurate, not rounded variables
        will be printed to the terminal.
        :param print_res: If true the un-rounded variables will be printed.
        """

        fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))

        fig.suptitle(r"\textbf{Relative flux vs relative time, with fitted curve}", fontsize=20)

        for ax, key, index in zip(axes, self.sup_data.keys(), self.graph_index):
            data = self.sup_data[key][index]

            tdata = data['RELATIVE_DATE']
            flux_data = data['RELATIVE_FLUX_WITHOUT_SYSTEMATICS']

            ax.plot(tdata, flux_data, 'o', c='y', label='Raw data')

            # -------------------------------------------------

            f_tdata = np.linspace(np.min(tdata), np.max(tdata), 300)

            c, A, sigma = self.sup_data[key][index]['res']
            fit = Process.gauss(f_tdata, c, A, sigma)

            ax.plot(f_tdata, fit, '-', label=fr'Fitted curve: {c=:.3f}, {A=:.3f}, $\sigma$={sigma:.3f}')

            # -------------------------------------------------

            ax.set_title(fr"{key} star's flux, index: {index}", fontsize=16)
            ax.set_xlabel(r"\textsc{relative time}", fontsize=14)
            ax.set_ylabel(r"\textsc{relative flux}", fontsize=14)

            ax.set_box_aspect(1)
            ax.legend()

            # -------------------------------------------------
            if print_res:
                print(f"Results of {key} star's, fitted curve.")
                print(f"   index {index}   |   file index {data['file_index']}")
                print(f"c = {float(c)}")
                print(f"A = {float(A)}")
                print(fr"sigma = {float(sigma)}")
                print('-----------------------------------------------')

        plt.tight_layout()
        plt.show()

    def sigma(self):
        """
        This function plots all the fitted sigma
        (width of the dip) values, distributed by star,
        and assigned with the data's file index.
        """

        plt.figure(figsize=(8, 6))

        sigma_data = [[data['res'][2], key] for key in self.sup_data.keys() for data in self.sup_data[key]]

        keys = list(self.sup_data.keys())
        colors = mpl.colormaps['tab20'].colors[:len(keys)]

        def color(name):
            for i, key in enumerate(keys):
                if name == key:
                    return colors[i]

        # Plot --------------------------------
        for i, (sigma, key) in enumerate(sigma_data):
            plt.bar(i, sigma, color=color(key))

        handles = [mplpat.Patch(color=colors[i], label=key) for i, key in enumerate(keys)]
        plt.legend(handles=handles)

        tick_labels = [data['file_index'] for key in self.sup_data.keys() for data in self.sup_data[key]]

        xticks = np.arange(0, len(sigma_data))
        plt.xticks(xticks, tick_labels, rotation='vertical')

        plt.title(r'\textbf{All fitted $\sigma$ of all measurements}', fontsize=16)
        plt.xlabel(r'\textsc{file index}', fontsize=14)
        plt.ylabel(r'\textsc{$\sigma$}', fontsize=14)

        plt.show()


if __name__ == '__main__':

    p = Process(dirPATH=directory)
    p.read_dir()
    p.FitGaussCurves()

    SuperData = p.Super_Data

    plot = Plot(SuperData)

    plot.all_flux()
    plot.fitted_curve()
    plot.sigma()
