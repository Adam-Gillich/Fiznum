import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import h5py
import cmocean  # Prettier cmaps, not on Jupyter, must be replaced with a stock one
import datetime as dt

# ----------------------------------
# File location
# ----------------------------------

file1 = 'nasa_data.HDF5'
file2 = 'mediterranean_coastline_lonlat.txt'


# ----------------------------------
# Requested functions
# ----------------------------------

def explore_hdf5(filename: str):
    """
    THis function gives a tour of the HDF file.
    Printing the group names and the datasets within,
     plus their shapes and types.
    :param filename: File location
    """

    def groups(name, obj):
        if isinstance(obj, h5py.Group):
            print(f'    {name}')

    def datasets(name, obj):
        if isinstance(obj, h5py.Dataset):
            print(f'    {name} {obj.shape} {obj.dtype}')

    hdf = h5py.File(filename, 'r')

    print(f'Now visiting {groups.__name__}:')
    hdf.visititems(groups)
    print('')
    print(f'Now visiting {datasets.__name__}:\n'
          f'    {{name}} {{obj.shape}} {{obj.dtype}}\n'
          f'    ------------------------------')
    hdf.visititems(datasets)


def read_precipitation_data(filename: str):
    """
    This function reads the HDF file, and returns the
    raw unprocessed longitude, latitude and precipitation data.
    :param filename: File location
    :return: longitude, latitude, precipitation
    """

    hdf = h5py.File(filename, 'r')

    hdfGrid = hdf['Grid']

    lon = np.array(hdfGrid['lon'])
    lat = np.array(hdfGrid['lat'])
    precipitation = np.array(hdfGrid['precipitation'])[0]  # Why the actual fuck is this nested in an array

    return lon, lat, precipitation


def mediterranean_subset(lon: np.ndarray, lat: np.ndarray, precipitation: np.ndarray):
    """
    This function extracts the mediterranean subset of the raw data.
    And arranges them in the structor of [[longitude, latitude, precipitation] ...],
    where every set is one point and its precipitation data attached to it.
    Then returns a numpy array.
    :param lon: Raw longitude data
    :param lat: Raw latitude data
    :param precipitation: Raw precipitation data
    :return: One neatly arranged array.
    """

    all_coast = read_coastline(file2)

    lon_bounds = (min(np.min(coast['longitude']) for coast in all_coast),
                  max(np.max(coast['longitude']) for coast in all_coast))

    lat_bounds = (min(np.min(coast['latitude']) for coast in all_coast),
                  max(np.max(coast['latitude']) for coast in all_coast))

    index_lon = [i for i, val in enumerate(lon) if lon_bounds[0] <= val <= lon_bounds[1]]
    index_lat = [i for i, val in enumerate(lat) if lat_bounds[0] <= val <= lat_bounds[1]]

    """
    TL;DR: Explanation of that oneliner below.
        For an easily understandable version scroll to the 
        bottom of this comment.
    
    So what I'm doing here and in multiple places in the code 
    is called 'list comprehension' basically this makes the 
    code a little easier to read because you can write just this:
    
    
    my_squared_list = [i**2 for i in data]
    
    
    Instead of this:
    
    my_squared_list = []  # You have to make an empty list beforehand
    
    for i in data:
        my_squared_list.append(i**2)
    
    # ---------------------------------------------
    
    Well as always I sometimes like to have a bit of fun 
    and make it extremely complex for no reason as you can see below.
    But here is what it does in a nicer way:
    
    
    medi_data = []

    for i in index_lon:
        for j in index_lat:
            a = lon[i]
            b = lat[j]
            c = precipitation[i, j]
            if c < 0.0:
                c = np.nan
            medi_data.append((a, b, c))
            
    
    // to check
        test_arr1 = np.array(medi_data)
        test_arr2 = np.array(medi_data2)
        eq = np.array_equal(test_arr1, test_arr2, equal_nan=True)
        print(eq)
    """

    def condition1(i, j):
        return lon[i], lat[j], precipitation[i, j]

    def condition2(i, j):
        return lon[i], lat[j], np.nan

    medi_data = [condition2(i, j) if precipitation[i, j] < 0.0 else condition1(i, j) for i in index_lon for j in index_lat]

    return np.array(medi_data)


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


def read_coastline(filename: str) -> list[dict]:
    """
    This function reads the coastline file, and processes it.
    :param filename: File location
    :return: The processed data, in the format of list[dict]
    """

    lon = []
    lat = []

    coast = []

    def AppendCoast():
        dict_entry = {f'{longitude.__name__}': lon, f'{latitude.__name__}': lat}
        coast.append(dict_entry)

    def longitude(val):
        lon.append(float(val))

    def latitude(val):
        lat.append(float(val))

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:
            split_lines = line.strip('\n').split(' ')
            if split_lines[0] == 'nan':
                AppendCoast()
                lon, lat = [], []
            else:
                longitude(split_lines[0])
                latitude(split_lines[1])

    """
    The function in an simpler structure:
    
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
    """

    return coast


def time_of_measurement(filename):
    """
    This function determines when the measurement took place,
    and prints the base reference time used by NASA, and the
    actual measurement time. The function returns this data
    in case it is needed later, but in this case it will not
    be needed.

    (It prints the beginning of the measurement, but with further
    digging, through the file it can be determined that the
    measurement took 30 minutes.)

    :param filename: File location
    :return: Measured time
    """

    hdf = h5py.File(filename, 'r')

    hdfGrid = hdf['Grid']

    t0 = dt.datetime(1980, 1, 6, 0, 0, 0, tzinfo=dt.timezone.utc)

    measure_time = t0 + dt.timedelta(seconds=int(hdfGrid['time'][0]))

    # ---------------------------------
    print(f"--------------------------------")
    print(f'Base reference time: [{dt.timezone.utc}]')
    print(f'{t0}\n')
    print(f'Measurement time:    [{dt.timezone.utc}]')
    print(f'{measure_time}')
    print(f"--------------------------------")

    return measure_time


# ----------------------------------
# Plot
# ----------------------------------

# Unused functions ---------------------------------------------------------------
def separate_data(medi_data):
    """
    Used to separate the structured data,
    to satisfy the specification.
    Although it won actually be used.
    :param medi_data: Structured data of mediterranean subset.
    :return: longitude, latitude, precipitation
    """

    return medi_data[:, 0], medi_data[:, 1], medi_data[:, 2]


def plot_mediterranean_precipitation(lon, lat, precipitation, coastline):
    """
    This is the requested plot function, that is a one-to-one copy
    of the one found in the Plot class. \n
    Instead of the requested
    functions the Plot version is preferred, but it can be
    somewhat easily toggled.
    :param lon: Longitude array
    :param lat: Latitude array
    :param precipitation: Precipitation array
    :param coastline: Coastline data, as list[dict]
    """

    SetTex()

    plt.figure(figsize=(18, 9))

    # Precipitation ----------------------------------------
    vmax = np.nanmax(precipitation)

    pre = plt.scatter(lon, lat, c=precipitation,
                      cmap=cmocean.cm.rain, vmin=0.0, vmax=vmax,  # add cmap='YlGnBu'
                      s=16, linewidths=0, marker='s', alpha=0.7)

    cbar = plt.colorbar(pre, pad=0.01, shrink=0.9)
    cbar.set_label(label=r'\textit{Precipitation}', size=16)

    # Coastlines ----------------------------------------
    all_position_data = Plot.extract_data(coastline, 'longitude', 'latitude')
    for lonlat_section in all_position_data:
        plt.plot(lonlat_section[0], lonlat_section[1], '-k', alpha=0.6)

    # Annotate ----------------------------------------
    xlim = [np.nanmin(lon), np.nanmax(lon)]
    ylim = [np.nanmin(lat), np.nanmax(lat)]

    plt.xlim(xlim)
    plt.ylim(ylim)

    plt.title(r'\textbf{Mediterrain precipitation}', size=18)
    plt.xlabel(r'\textsc{longitude}', size=14)
    plt.ylabel(r'\textsc{latitude}', size=14)

    plt.show()
# --------------------------------------------------------------------------------


class Plot:
    """This class does the plotting"""

    def __init__(self, mediterrain_subset_data, coastline_data):
        self.medi_data = mediterrain_subset_data
        self.coast = coastline_data

        SetTex()

    @staticmethod
    def extract_data(iterable: list[dict], key1: str, key2: str) -> np.ndarray:
        """
        Function for extracting processable data for plt.plot() function.
        :param iterable: Iterable data, in the form list[dict]
        :param key1: Key of x-axis
        :param key2: Key of y-axis
        :return: Returns np.ndarray, and if the conversion fails, then raw list
        """

        data = [[i[key1], i[key2]] for i in iterable]

        try:
            return np.array(data)
        except ValueError:
            return data

    def mediterranean_precipitation(self):
        """
        This method does the plotting.

        Important thing to note, that the mediterrain_subset_data
        is incoming in the form [[longitude, latitude, precipitation] ...]
        """

        plt.figure(figsize=(18, 9))

        # Precipitation ----------------------------------------
        vmax = np.nanmax(self.medi_data[:, 2])

        pre = plt.scatter(self.medi_data[:, 0], self.medi_data[:, 1], c=self.medi_data[:, 2],
                          cmap=cmocean.cm.rain, vmin=0.0, vmax=vmax,  # add cmap='YlGnBu'
                          s=16, linewidths=0, marker='s', alpha=0.7)

        cbar = plt.colorbar(pre, pad=0.01, shrink=0.9)
        cbar.set_label(label=r'\textit{Precipitation}', size=16)

        # Coastlines ----------------------------------------
        all_position_data = self.extract_data(self.coast, 'longitude', 'latitude')
        for lonlat_section in all_position_data:
            plt.plot(lonlat_section[0], lonlat_section[1], '-k', alpha=0.6)

        # Annotate ----------------------------------------
        xlim = [np.nanmin(self.medi_data[:, 0]), np.nanmax(self.medi_data[:, 0])]
        ylim = [np.nanmin(self.medi_data[:, 1]), np.nanmax(self.medi_data[:, 1])]

        plt.xlim(xlim)
        plt.ylim(ylim)

        plt.title(r'\textbf{Mediterrain precipitation}', size=18)
        plt.xlabel(r'\textsc{longitude}', size=14)
        plt.ylabel(r'\textsc{latitude}', size=14)

        plt.show()


if __name__ == '__main__':
    # Explore
    explore_hdf5(file1)

    # Extract data
    lon, lat, precipitation = read_precipitation_data(file1)
    coast_data = read_coastline(file2)

    # Make mediterranean subset
    medi_data = mediterranean_subset(lon, lat, precipitation)

    # Plot init
    plot = Plot(medi_data, coast_data)

    # Plot
    plot.mediterranean_precipitation()

    # Figure out when the measurement was taken
    time_of_measurement(file1)

    # --------------------------------------------------------------------------
    # The shadow realm

    if False:
        lon, lat, pre = separate_data(medi_data)

        plot_mediterranean_precipitation(lon, lat, pre, coast_data)
