import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import requests
import io

# ----------------------------------
# URL
# ----------------------------------

URL = 'https://www.ksh.hu/stadat_files/tte/hu/tte0008.html'


def read_url(url):
    """
    Reads the KSH data, from a URL.
    :param url: Given url
    :return: The renamed dataframe
    """

    response = requests.get(url)

    # The page contains one table with two header rows
    raw = pd.read_html(io.StringIO(response.text), header=[0, 1])[0]

    raw = raw.rename(columns={'A kutató-fejlesztő helyek kutatóinak tényleges, állományi létszáma, fő': 'Total',
                              'Ebből: nők létszáma, fő': 'Women',
                              '25 évnél fiatalabb': '25-',
                              '65 éves vagy idősebb': '65+',
                              'Összesen': 'Total',
                              '25–34': '25-34',
                              '35–44': '35-44',
                              '45–54': '45-54',
                              '55–64': '55-64'})

    return raw


def SetTex():
    """
    Sets TeX fonts.
    """

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


def WhenDidShirnk(df):
    """
    This function finds, in which year
    did the number of researchers shrink
    :param df: Input dataframe
    """

    years = df[('Év', 'Év')]
    totals = df[('Total', 'Total')]

    for i in range(0, len(totals) - 1):
        if totals[i] > totals[i + 1]:
            print('-' * 50)
            print(f'In year {years[i + 1]}, the number of researchers shrink:')
            print(f'   {years[i]}: {totals[i]}')
            print(f'   {years[i + 1]}: {totals[i + 1]}')
            found = True

    try:
        if not found:
            print(f'The numbers always grew.')
    except UnboundLocalError or NameError:
        print('-' * 25)


def WomenRatio(df):
    """
    This function finds the highest, and lowest
    Women to Total ratio. Amongst the under 35 age range.
    :param df: Input dataframe
    """

    years = df[('Év', 'Év')]

    def to_numeric(col):
        return df[col].astype(str).str.replace(' ', '', regex=False).astype(int)

    women_25 = to_numeric(('Women', '25-'))
    women_25_34 = to_numeric(('Women', '25-34'))
    total_25 = to_numeric(('Total', '25-'))
    total_25_34 = to_numeric(('Total', '25-34'))

    ratio_25 = women_25 / total_25
    ratio_25_34 = women_25_34 / total_25_34

    # For max: pick the group whose peak ratio is larger
    if ratio_25.max() >= ratio_25_34.max():
        ratio_max, group_max = ratio_25, '<25'
    else:
        ratio_max, group_max = ratio_25_34, '25-34'

    # For min: pick the group whose trough ratio is smaller
    if ratio_25.min() <= ratio_25_34.min():
        ratio_min, group_min = ratio_25, '<25'
    else:
        ratio_min, group_min = ratio_25_34, '25-34'

    print('-' * 50)
    print(f'Highest women ratio in under-35 (group: {group_max}): \n'
          f'   {years.iloc[ratio_max.argmax()]}: {ratio_max.max():.2%}')
    print(f'Lowest  women ratio in under-35 (group: {group_min}): \n'
          f'   {years.iloc[ratio_min.argmin()]}: {ratio_min.min():.2%}')


def MenRatio(df):
    """
    This function finds the largest ratio change in Men,
    in the more than 35 age range.
    :param df: Input dataframe
    """

    years = df[('Év', 'Év')]

    def to_numeric(col):
        return df[col].astype(str).str.replace(' ', '', regex=False).astype(int)

    keys = ['35-44', '45-54', '55-64', '65+']

    best_increase = 0
    best_year = None
    best_group = None

    for key in keys:
        women = to_numeric(('Women', key))
        total = to_numeric(('Total', key))
        men_ratio = (total - women) / total

        delta = men_ratio.diff()  # year-over-year change
        idx = delta.argmax()  # index of largest increase

        if delta.iloc[idx] > best_increase:
            best_increase = delta.iloc[idx]
            best_year = years.iloc[idx]
            best_group = key

    print('-' * 50)
    print(f'Largest increase in men\'s ratio in 35+ (group: {best_group}): \n'
          f'   {best_year}: +{best_increase:.2%}')


class Plot:

    def __init__(self, data):
        self.df = data
        SetTex()

    def to_numeric(self, col):
        return self.df[col].astype(str).str.replace(' ', '', regex=False).astype(int)

    def total_vs_time(self):
        """
        This function plots the total number of researchers as a function of time.
        """

        years = self.df[('Év', 'Év')]
        totals = self.to_numeric(('Total', 'Total'))

        plt.bar(years, totals, zorder=2, width=0.8)

        plt.xticks(years, rotation=45)
        plt.title(r'\textbf{Total number of researchers vs time}', size=16)
        plt.xlabel(r'\textsc{years}', size=14)
        plt.ylabel(r'\textsc{number of researchers}', size=14)

        plt.grid(zorder=1)
        plt.tight_layout()
        plt.show()

    def women_ratios(self):
        """
        This function plots all the women age groups as a  function of time.
        """

        plt.figure(figsize=(16*(7/9), 9*(7/9)))

        years = self.df[('Év', 'Év')]

        keys = ['25-', '25-34', '35-44', '45-54', '55-64', '65+']

        for key in keys:
            try:
                women = np.array([int(''.join([k for k in i if k != ' '])) for i in self.df[('Women', key)]],
                                 dtype=np.float64)
            except TypeError:
                women = np.array(df[('Women', key)])

            total = np.array([int(''.join([k for k in i if k != ' '])) for i in self.df[('Total', key)]],
                             dtype=np.float64)

            ratio = women / total

            plt.plot(years, ratio, '-o', markersize=3, label=f'{key} age group.')

            plt.title(r'\textbf{Ratio of women researchers throughout time, in different age groups}', size=20)
            plt.xlabel(r'\textsc{years}', size=16)
            plt.ylabel(r'\textsc{ratio} $[women/total]$', size=16)

        plt.grid()
        plt.legend()
        plt.show()

    def alle_forscher_geschlecht(self):
        """
        This function plots all researchers as a function of time, with the genders separated.
        """

        years = self.df[('Év', 'Év')]
        women = self.to_numeric(('Women', 'Total'))
        total = self.to_numeric(('Total', 'Total'))
        men = total - women

        curr_df = pd.DataFrame({'Men': men.values, 'Women': women.values}, index=years.values)

        curr_df.plot(kind='bar', stacked=True, figsize=(11, 6), color=['steelblue', 'salmon'], zorder=2)

        plt.xticks(rotation=45)
        plt.title(r'\textbf{Total number of researchers by gender}', size=16)
        plt.xlabel(r'\textsc{years}', size=14)
        plt.ylabel(r'\textsc{number of researchers}', size=14)

        plt.grid(axis='y', ls='--', zorder=1)
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    df = read_url(URL)

    WhenDidShirnk(df)
    WomenRatio(df)
    MenRatio(df)

    plot = Plot(df)
    plot.total_vs_time()
    plot.women_ratios()
    plot.alle_forscher_geschlecht()
