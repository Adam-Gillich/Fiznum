# Azt a szart (file) a jupyteren belülről kell elérni

import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime


# --------------- Counter (inlined from collections) ---------------

class Counter(dict):
    """Dict subclass for counting hashable items."""

    def __init__(self, iterable=None, /, **kwds):
        super().__init__()
        self.update(iterable, **kwds)

    def __missing__(self, key):
        return 0

    def most_common(self, n=None):
        items = sorted(self.items(), key=lambda x: x[1], reverse=True)
        if n is None:
            return items
        return items[:n]

    def update(self, iterable=None, /, **kwds):
        if iterable is not None:
            if isinstance(iterable, dict):
                for elem, count in iterable.items():
                    self[elem] = count + self.get(elem, 0)
            else:
                for elem in iterable:
                    self[elem] = self.get(elem, 0) + 1
        if kwds:
            self.update(kwds)

    def __repr__(self):
        if not self:
            return f'{self.__class__.__name__}()'
        d = dict(self.most_common())
        return f'{self.__class__.__name__}({d!r})'


# ----------------------------------
# File locations
# ----------------------------------

file1 = "/v/courses/2026-afizikanumerikusmdszerei12026.public/data/mediterranean_coastline_lonlat.txt"
file2 = "/v/courses/2026-afizikanumerikusmdszerei12026.public/data/earthquakes_mediterranean_2024.csv"

# ----------------------------------
# Requested functions
# ----------------------------------


def read_coastline(filename: str):
    """
    This function reads the coastline file, and processes it.
    :param filename: File location
    :return: The processed data, in the format of list[dict]
    """

    lon = []
    lat = []

    coast = []

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:
            split_lines = line.split(' ')

            if split_lines[0] == 'nan':

                dict_entry = {'longitude': lon, 'latitude': lat}
                coast.append(dict_entry)

                lon, lat = [], []
            else:
                lon.append(float(split_lines[0]))
                lat.append(float(split_lines[1]))

    return coast



def _parse_csv_line(line: str) -> list[str]:
    """
    Parse a single CSV line into a list of fields, correctly handling quoted fields
    that may contain commas.
    :param line: A single raw line string from a CSV file (without the trailing newline).
    :return: A list of field strings parsed from the line.
    """

    fields = []
    current = []
    in_quotes = False
    for ch in line:
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == ',' and not in_quotes:
            fields.append(''.join(current))
            current = []
        else:
            current.append(ch)
    fields.append(''.join(current))
    return fields


def read_earthquakes(filename: str):
    """
    This function reads and processes the earthquake file.
    :param filename: File location
    :return: The processed data, in the format of list[dict]
    """

    earthquakes = []

    with open(filename, 'r', encoding='utf-8') as file:
        header_line = file.readline().strip()
        headers = header_line.split(',')
        col = {name: idx for idx, name in enumerate(headers)}

        for line in file:
            line = line.strip()
            if not line:
                continue
            row = _parse_csv_line(line)
            earthquakes.append({
                'time':      datetime.datetime.strptime(row[col['time']], '%Y-%m-%dT%H:%M:%S.%fZ'),
                'latitude':  float(row[col['latitude']]),
                'longitude': float(row[col['longitude']]),
                'depth':     float(row[col['depth']]),
                'magnitude': float(row[col['mag']]),
                'place':     row[col['place']],
            })

    return earthquakes

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


def PlaceOfMostEQs(earthquakes: list[dict]):
    """
    This function calculates the most common place, where earthquakes happen.
    :param earthquakes: Data from earthquakes file
    :return: Tuple of name, occurrence, and list of indexes of the most common place
    """

    def condition(eq):
        return eq['place'].split(' ')[4] + ' ' + eq['place'].split(' ')[5]

    data = Counter(condition(eq) for eq in earthquakes)
    name, occurrence = data.most_common(1)[0]

    index = []

    for i, eq in enumerate(earthquakes):
        if condition(eq) == name:
            index.append(i)
            if len(index) == occurrence:
                break

    return name, occurrence, index


def AvgLocation(earthquakes: list[dict], index: list):
    """
    This function calculates the average position of the most common place.
    :param earthquakes: Data from earthquakes file
    :param index: List of indexes of the most common place
    :return: Tuple of average positions
    """

    lat = [earthquakes[i]['latitude'] for i in index]
    lon = [earthquakes[i]['longitude'] for i in index]

    avg_lat = sum(lat) / len(lat)
    avg_lon = sum(lon) / len(lon)

    return avg_lat, avg_lon


def PrintMostCommon(earthquakes: list[dict]):
    """
    This function prints and returns the
    combined result of the above two functions
    :param earthquakes: Data from earthquakes file
    :return: Tuple of processed results
    """

    name, occurrence, index = PlaceOfMostEQs(earthquakes)

    avg_lat, avg_lon = AvgLocation(earthquakes, index)

    print(f"Most common place found!\n"
          f"{name!r} occurred {occurrence} times.\n"
          f"Their average positions:\n"
          f"longitude | latitude\n"
          f"{avg_lon: ^9.2f} | {avg_lat: ^8.2f}")

    return name, occurrence, avg_lon, avg_lat

# ----------------------------------
# Plot
# ----------------------------------


class Plot:
    """This class orchestrates the plotting functions"""

    def __init__(self, earthquakes_data, coast_data):
        self.earthquakes = earthquakes_data
        self.coast = coast_data

        self.most_common = PrintMostCommon(self.earthquakes)

        SetTex()

    @staticmethod
    def extract_data(iterable: list[dict], key1: str, key2: str):
        """
        Function for extracting processable data for plt.plot() function.
        :param iterable: Iterable data, in the form list[dict]
        :param key1: Key of x-axis
        :param key2: Key of y-axis
        :return: Returns np.ndarray, and if the conversion fails, then raw list
        """

        col1 = [i[key1] for i in iterable]
        col2 = [i[key2] for i in iterable]
        return col1, col2

    def Mag_and_Depth(self) -> None:
        """
        This plots the magnitude and depth as a function of time.
        """

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.2))

        times, magnitudes = self.extract_data(self.earthquakes, 'time', 'magnitude')

        ax1.bar(times, magnitudes)
        ax1.set_title(r'\textbf{Magnitude as a function of time}', size=18)
        ax1.set_xlabel(r'\textsc{time}', size=14, loc='left')
        ax1.set_ylabel(r'\textsc{magnitude}', size=14)

        # ------------------------------------------------

        times, depths = self.extract_data(self.earthquakes, 'time', 'depth')

        ax2.bar(times, depths, color='crimson')
        ax2.set_title(r'\textbf{Depth as a function of time}', size=18)
        ax2.set_xlabel(r'\textsc{time}', size=14, loc='left')
        ax2.set_ylabel(r'\textsc{depth}', size=14)

        plt.tight_layout()
        plt.show()

    def Coastline(self) -> None:
        """
        This plots the map and the earthquakes
        on the map with the average position
        of the most common place in red.
        """

        coast_lons, coast_lats = self.extract_data(self.coast, 'longitude', 'latitude')

        eq_lons, eq_lats = self.extract_data(self.earthquakes, 'longitude', 'latitude')
        magni_data = [i['magnitude'] for i in self.earthquakes]

        plt.figure(figsize=(16, 9))

        for lon_section, lat_section in zip(coast_lons, coast_lats):
            plt.plot(lon_section, lat_section, '-')

        for lon, lat, mag in zip(eq_lons, eq_lats, magni_data):
            plt.plot(lon, lat, 'yo', markersize=mag * 2)

        plt.plot(self.most_common[2], self.most_common[3], 'or', markersize=7,
                 label=f'The most common place is\n'
                       f'{self.most_common[0]} which occurred {self.most_common[1]} times')

        plt.annotate('there',
                     xy=(self.most_common[2], self.most_common[3]),
                     xytext=(self.most_common[2] + 5, self.most_common[3] - 5),
                     fontsize=12,
                     arrowprops=dict(arrowstyle='->', color='red'),
                     color='red')

        plt.title(r'\textbf{Position of earthquakes on the map}', size=18)
        plt.xlabel(r'\textsc{longitude}', size=14)
        plt.ylabel(r'\textsc{latitude}', size=14)

        plt.legend(fontsize=14)
        plt.show()


if __name__ == '__main__':

    co_data = read_coastline(file1)
    eq_data = read_earthquakes(file2)

    plot = Plot(eq_data, co_data)

    plot.Mag_and_Depth()

    plot.Coastline()
