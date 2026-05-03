import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import requests, io

# ----------------------------------
# File / URL locations
# ----------------------------------

file = 'UFO_eszlelesek.csv'
url = 'https://developers.google.com/public-data/docs/canonical/states_csv'


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


def HaversineDistance(row: pd.Series) -> float:
    """
    Calculates the great-circle distance between a UFO sighting and the
    centroid of its state using the Haversine formula.
    :param row: A row of the merged DataFrame containing 'szelesseg',
                'hosszusag', 'latitude' (centroid) and 'longitude' (centroid).
    :return: Distance in kilometres.
    """

    R = 6371.0

    lat1 = np.radians(row['szelesseg'])
    lon1 = np.radians(row['hosszusag'])
    lat2 = np.radians(row['latitude'])
    lon2 = np.radians(row['longitude'])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c


# ----------------------------------
# Data loading and preprocessing
# ----------------------------------

def read_ufo(filename: str) -> pd.DataFrame:
    """
    Loads the UFO sightings CSV and converts columns to their proper types.
    :param filename: Path to the CSV file.
    :return: Cleaned DataFrame.
    """

    df = pd.read_csv(filename, low_memory=False)  # False, for err msg said so

    df['idopont'] = pd.to_datetime(df['idopont'], errors='coerce')
    df['szelesseg'] = pd.to_numeric(df['szelesseg'], errors='coerce')
    df['hosszusag'] = pd.to_numeric(df['hosszusag'], errors='coerce')
    df['idotartam (s)'] = pd.to_numeric(df['idotartam (s)'], errors='coerce')

    return df


# ----------------------------------
# Analysis functions
# ----------------------------------

def EarliestSighting(df: pd.DataFrame) -> pd.Series:
    """
    Returns the row corresponding to the earliest UFO sighting.
    :param df: UFO sightings DataFrame.
    :return: The row with the minimum 'idopont' value.
    """

    earliest = df.loc[df['idopont'].idxmin()]

    print("─" * 50)
    print("Earliest UFO sighting:")
    print(f"  Date/time : {earliest['idopont']}")
    print(f"  City      : {earliest['varos']}, {earliest['allam']}, {earliest['orszag']}")
    print(f"  Duration  : {earliest['idotartam (s)']} s")
    print("─" * 50)

    return earliest


def CountryStats(df: pd.DataFrame):
    """
    Prints and returns country-level statistics:
      - number of distinct countries,
      - the country with the most sightings,
      - how many times more sightings it had than all others combined.
    Rows with missing 'orszag' values are excluded.
    :param df: UFO sightings DataFrame.
    :return: Tuple of (n_countries, top_country, ratio).
    """

    valid = df.dropna(subset=['orszag'])

    counts = valid['orszag'].value_counts()
    n_countries = counts.nunique()
    top_country = counts.index[0]
    top_count = counts.iloc[0]
    rest_count = counts.iloc[1:].sum()
    ratio = top_count / rest_count

    print("Country statistics:")
    print(f"  Number of distinct countries: {n_countries}")
    print(f"  Country with most sightings:  {top_country!r} ({top_count} sightings)")
    print(f"  Ratio to the rest:            {ratio:.2f}x")
    print("─" * 50)

    return n_countries, top_country, ratio


def MergeWithStates(df: pd.DataFrame, states_url: str) -> pd.DataFrame:
    """
    Fetches the US-states centroid table from the web and merges it with the
    American UFO sightings.
    :param df: Full UFO sightings DataFrame.
    :param states_url: URL of the states CSV table.
    :return: Merged DataFrame containing sightings and state centroid coordinates.
    """

    response = requests.get(states_url)

    states_df = pd.read_html(io.StringIO(response.text), header=0)[0]

    # Keep only US sightings; the 'allam' column holds two-letter abbreviations
    us_df = df[df['orszag'] == 'us'].copy()
    us_df['allam'] = us_df['allam'].str.upper()

    # The states table uses the column 'abbreviation' for the state code
    merged = us_df.merge(states_df, left_on='allam', right_on='state', how='inner')

    return merged


def MostSightingsState(merged: pd.DataFrame):
    """
    Determines which US state had the most UFO sightings.
    :param merged: Merged DataFrame of US sightings with state centroids.
    :return: The two-letter state abbreviation with the most sightings.
    """

    counts = merged['allam'].value_counts()
    top_state = counts.index[0]

    print("US state analysis:")
    print(f"  US state with the most sightings: {top_state!r} ({counts.iloc[0]} sightings)")
    print("─" * 50)

    return top_state


# ----------------------------------
# Plot
# ----------------------------------

class Plot:
    """
    Orchestrates the visualisation of the UFO distance distribution.
    :param merged:    Merged DataFrame (US sightings + state centroids).
    :param top_state: Two-letter abbreviation of the state to analyse.
    """

    def __init__(self, merged, top_state: str):
        self.merged = merged
        self.top_state = top_state

        SetTex()

    def distance_distribution(self) -> None:
        """
        Plots the distribution of distances between individual UFO sightings
        and the centroid of the state with the most sightings.
        """

        state_data = self.merged[self.merged['allam'] == self.top_state].copy()

        state_data['distance_km'] = state_data.apply(HaversineDistance, axis=1)

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.hist(state_data['distance_km'].dropna(), bins=100, edgecolor='black', color='steelblue')

        ax.set_title(
            r'\textbf{Distribution of sighting distances from state centroid}'
            f' --- {self.top_state.upper()}',
            size=20
        )
        ax.set_xlabel(r'\textsc{distance} [km]', size=16)
        ax.set_ylabel(r'\textsc{count}', size=16)

        plt.tight_layout()
        plt.show()


# ----------------------------------
# Main
# ----------------------------------

if __name__ == '__main__':
    # --- Load data ---
    ufo = read_ufo(file)

    # --- Earliest sighting ---
    EarliestSighting(ufo)

    # --- Country statistics ---
    CountryStats(ufo)

    # --- Merge with US states ---
    merged = MergeWithStates(ufo, url)

    # --- State with most sightings ---

    top_state = MostSightingsState(merged)

    # --- Plot ---
    plot = Plot(merged, top_state)
    plot.distance_distribution()

    '''
    Interpretation:
    The distribution of distances from the state centroid shows a roughly
    log-normal shape: most sightings cluster within a few hundred kilometres
    of the centroid, with a long tail extending further out. This mirrors the
    population density pattern — the majority of residents (and therefore
    observers) live near the larger urban centres, which tend to be close to
    the geometric centre of densely populated states such as California.
    '''
