import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# ----------------------------------
# File locations
# ----------------------------------

contestants_file = 'contestants.csv'
votes_file = 'votes.csv'


# ----------------------------------
# Helper functions
# ----------------------------------

def SetTex():
    """Sets TeX fonts."""
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cm'


# ----------------------------------
# Requested functions
# ----------------------------------

def FixAbbreviation(contestants):
    """
    Makes various checks and corrections.
        Starting with assigning an ID to andorra. Then locating
        all country names that are assigned to an ID and chooses
        the most common of them in the canonical dataframe (df).
        Then we check where is country name in place of ID
        (Poland—Poland, instead of pl—Poland) and correct them.
        Quick check whether  everything is correct, then apply
        canonized country names.
    :param contestants: Raw contestants DataFrame
    :return: Fixed contestants DataFrame
    """
    # Assign known missing IDs
    contestants.loc[contestants['to_country'] == 'Andorra', 'to_country_id'] = 'ad'

    # Canonicalise: keep the most frequent to_country for each to_country_id
    canonical = (
        contestants.groupby('to_country_id')['to_country']
        .agg(lambda x: x.value_counts().index[0])
        .reset_index()
        .rename(columns={'to_country': 'to_country_canonical'})
    )

    # Fix to_country_id: replace remaining full country names with their 2-letter abbreviations
    name_to_id = canonical[canonical['to_country_id'].str.len() == 2].set_index('to_country_canonical')['to_country_id']
    still_long = contestants['to_country_id'].str.len() > 2
    contestants.loc[still_long, 'to_country_id'] = contestants.loc[still_long, 'to_country_id'].map(name_to_id)
    contestants = contestants.merge(canonical, on='to_country_id', how='left')

    # Locate missing, IDs or countries ---------------------------------------
    mismatches = contestants.loc[contestants['to_country'] != contestants['to_country_canonical'], ['to_country_id', 'to_country', 'to_country_canonical']]
    if not mismatches.empty:  # If mismatches is empty, all is well
        print(f'Remaining mismatches:\n{mismatches.to_string()}')

    # Correct countries ------------------------------------------------------
    contestants['to_country'] = contestants['to_country_canonical']
    contestants = contestants.drop(columns=['to_country_canonical'])  # Drop the now redundant col

    return contestants


def Winners_70s(contestants):
    """
    Prints the Eurovision winners of the 1970s, sorted by year.
    :param contestants: Fixed contestants DataFrame
    """

    winners = (
        contestants[
            (contestants['year'] >= 1970) &
            (contestants['year'] <= 1979) &
            (contestants['place_contest'] == 1)
            ]
        .sort_values('year')
        [['year', 'performer', 'to_country', 'song']]
    )

    print('—' * 60)
    print("Winners in the '70s (sorted by year):")
    print(winners.to_string(index=False))


def BestHungarianResult(contestants):
    """
    Finds and prints the best-ever result of a Hungarian contestant.
    :param contestants: Fixed contestants DataFrame
    """

    hungary = contestants[contestants['to_country_id'] == 'hu'].copy()
    best_hu = hungary.loc[hungary['place_contest'].idxmin()]

    print('—' * 60)
    print('Best Hungarian result:')
    print(f"   Year: {best_hu['year']},  Place: {best_hu['place_contest']},  Performer: {best_hu['performer']}")


def TopPointGiversForHungary(contestants, votes):
    """
    For each Hungarian Grand Final entry, prints which country gave the most
    points (total_point) and how many. Ties are all listed.
    Country names are used, not IDs.
    :param contestants: Fixed contestants DataFrame
    :param votes: Votes DataFrame
    """

    hu_finals = contestants[(contestants['to_country_id'] == 'hu')][['year', 'performer']].copy()

    hu_votes = votes[(votes['to_country_id'] == 'hu') & (votes['round'] == 'final')][
        ['year', 'from_country_id', 'total_points']].copy()

    hu_votes = hu_votes.merge(hu_finals, on='year', how='inner')

    hu_votes_max = hu_votes.groupby(['year', 'performer'])['total_points'].transform('max')
    best_givers = hu_votes[hu_votes['total_points'] == hu_votes_max].copy()

    id_to_name = (
        contestants[['to_country_id', 'to_country']]
        .drop_duplicates()
        .set_index('to_country_id')['to_country']
    )
    best_givers['from_country'] = best_givers['from_country_id'].map(id_to_name)

    result = best_givers[['year', 'performer', 'from_country', 'total_points']].sort_values(['year', 'from_country'])

    print('—' * 60)
    print('Top point-giving country for each Hungarian finalist (Grand Final):')
    print(result.to_string(index=False))


def plot_byealex_pie(contestants, votes):
    """
    Draws a pie chart of the points ByeAlex received in the Grand Final,
    broken down by voting country (identified by country code).
    :param contestants: Fixed contestants DataFrame
    :param votes: Votes DataFrame
    """
    byealex_year = (contestants[contestants['performer'].str.contains('ByeAlex', case=False, na=False)]['year'].iloc[0])

    byealex_votes = votes[
        (votes['to_country_id'] == 'hu') &
        (votes['round'] == 'final') &
        (votes['year'] == byealex_year) &
        (votes['total_points'] > 0)
        ].copy()

    fig, ax = plt.subplots(figsize=(8 * 1.25, 6 * 1.25))

    sclabels = list(map(lambda i: fr'\textsc{{{i}}}', byealex_votes['from_country_id']))
    # ax.pie(byealex_votes['total_points'], labels=sclabels,
    #       autopct='%1.1f%%', startangle=90, rotatelabels=True, textprops={'size': 20}, pctdistance=.8)

    patches, texts, autotexts = ax.pie(
        byealex_votes['total_points'], labels=sclabels,
        autopct='%1.1f%%', startangle=90, textprops={'size': 20}, pctdistance=.8
    )
    for at, patch in zip(autotexts, patches):
        angle = (patch.theta1 + patch.theta2) / 2  # midpoint angle of wedge
        at.set_rotation(angle + 180 if 180 < angle < 270 else (angle if angle > 180 else angle + 180))

    ax.set_title(fr'\textbf{{ByeAlex ({byealex_year}) — points received in the Grand Final by country}}', size=20)

    plt.tight_layout()
    plt.show()


# ----------------------------------
# Main
# ----------------------------------
if __name__ == '__main__':
    contestants = pd.read_csv(contestants_file)
    votes = pd.read_csv(votes_file)

    contestants = FixAbbreviation(contestants)

    Winners_70s(contestants)

    BestHungarianResult(contestants)

    TopPointGiversForHungary(contestants, votes)

    SetTex()
    plot_byealex_pie(contestants, votes)
