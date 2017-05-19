"""Helper functions for Fitbit data analysis."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

import os

import numpy as np
import pandas as pd


#------------------------
# List relevant filenames
#------------------------

fitbit_basedir = '../data/_MASTER/'

filenames = {'heart-rate': 'MASTER_heart-rate.csv',
             'mult-measures': 'MASTER_multiple-measures.csv',
             'resting-heart-rate': 'MASTER_resting-hr.csv',
             'sleep': 'MASTER_sleep.csv',
             'roster': '../rosters/roster_Feb16.xlsx'}

for measure, filename in filenames.items():
    if measure != 'roster':
        filenames[measure] = os.path.join(fitbit_basedir, filename)



#-------------------------
# Define excluded subjects
#-------------------------
#
# Below Fitbit usage threshold of 75%:
#     MBL094, MBL011, MBL045, MBL052, MBL042, MBL016, MBL093, MBL066, MBL028,
#     MBL059
#
# Failed or dropped PE (and in exercise group):
#     MBL016, MBL023, MBL045, MBL059, MBL066
#
# Missed 5 of 9 quizzes:
#     MBL048, MBL064

excluded_subjects = ['MBL094', 'MBL011', 'MBL045', 'MBL052', 'MBL042',
                     'MBL016', 'MBL093', 'MBL066', 'MBL028', 'MBL059',
                     'MBL016', 'MBL023', 'MBL045', 'MBL059', 'MBL066',
                     'MBL048', 'MBL064',]
excluded_subjects = list(set(excluded_subjects))



#--------------------------------
# Define the dates of assessments
#--------------------------------
#
# Do not include quiz 9 and the final.

assessment_dates = [
    ('Quiz_1', '2016-09-15'),
    ('Quiz_2', '2016-09-22'),
    ('Quiz_3', '2016-09-29'),
    ('Midterm_1', '2016-10-05'),  # 11:05 am to 11:55 am
    ('Quiz_4', '2016-10-13'),
    ('Quiz_5', '2016-10-20'),
    ('Quiz_6', '2016-10-27'),
    ('Midterm_2', '2016-11-02'),  # 11:05 am to 11:55 am
    ('Quiz_7', '2016-11-10'),
    ('Quiz_8', '2016-11-17'),
    ('Midterm_3', '2016-11-30'),
    # ('Quiz_9', '2016-12-08'),
    # ('Final', '2016-12-20'),
]



#------------------
# Data load helpers
#------------------

def to_datetime_inplace(df, *columns, **kwds):
    """Convert columns to datetime format in-place."""
    for c in columns:
        df.loc[:, c] = pd.to_datetime(df.loc[:, c], **kwds)


def remove_excluded_subjs(df, to_exclude):
    """Return pd.DataFrame with specified subjects removed."""
    return df[~df.subjectID.isin(to_exclude)]


def check_subjects_removed(df, to_exclude):
    """Raise error if subject in `to_exclude` is in `df.subjectID`."""
    if pd.Series(list(to_exclude)).isin(df.subjectID).any():
        raise Exception("Some subjects not excluded.")



#-------------
# Data loaders
#-------------

def load_heart_rate_data(filepath=filenames['heart-rate'], exclude=True):
    """Return pd.DataFrame of heart rate data."""
    df = pd.read_csv(filepath)
    df.loc[:, 'bpm'].replace(0, np.nan, inplace=True)
    to_datetime_inplace(df, 'dateTime')

    if exclude:
        df = remove_excluded_subjs(df, excluded_subjects)
        check_subjects_removed(df, excluded_subjects)

    return df


def load_mult_measures_data(filepath=filenames['mult-measures'], exclude=True):
    """Return pd.DataFrame of multiple measures data."""
    df = pd.read_csv(filepath)
    to_datetime_inplace(df, 'dateTime')

    if exclude:
        df = remove_excluded_subjs(df, excluded_subjects)
        check_subjects_removed(df, excluded_subjects)

    return df


def load_resting_heart_rate_data(filepath=filenames['resting-heart-rate'],
                                 exclude=True):
    """Return pd.DataFrame of resting heart rate data."""
    df = pd.read_csv(filepath)
    to_datetime_inplace(df, 'date')

    if exclude:
        df = remove_excluded_subjs(df, excluded_subjects)
        check_subjects_removed(df, excluded_subjects)

    return df


def load_sleep_data(filepath=filenames['sleep'], exclude=True):
    """Return pd.DataFrame of sleep data."""
    df = pd.read_csv(filepath)
    to_datetime_inplace(df, 'date', 'startDateTime', 'endDateTime')
    df.set_index('date', drop=False, inplace=True)

    if exclude:
        df = remove_excluded_subjs(df, excluded_subjects)
        check_subjects_removed(df, excluded_subjects)

    return df


def load_roster(filepath=filenames['roster'], exclude=True):
    """Return pd.DataFrame of roster data."""
    df = pd.read_excel(filepath)
    df.set_index('subjectID', drop=False, inplace=True)

    # Replace spaces and special characters in column names with underscore.
    df.rename(columns=lambda x: x.replace(" ", "_"), inplace=True)
    df.rename(columns=lambda x: x.replace("?", "_"), inplace=True)
    df.rename(columns=lambda x: x.replace("(", "_"), inplace=True)
    df.rename(columns=lambda x: x.replace(")", "_"), inplace=True)

    # Remove some information.
    df.drop(['account_email', 'lastname', 'firstname'], axis=1, inplace=True)
    df.replace(to_replace="X", value=np.nan, inplace=True)
    df.drop(['Quiz_9', 'Final'], axis=1, inplace=True)

    # Get sum of all assessment scores per subject.
    assessments = [j for j, _ in assessment_dates]
    df.loc[:, 'overall_score'] = df.loc[:, assessments].sum(axis=1)

    if exclude:
        df = remove_excluded_subjs(df, excluded_subjects)
        check_subjects_removed(df, excluded_subjects)

    return df
