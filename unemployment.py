import numpy as np
import math
import pandas as pd
from rapidfuzz import process, fuzz
import streamlit as st
import random

def grades_dist():
    '''
    Returns a distribution that will be used to
    assign grades to graduate agents
    '''
    awarded_degrees_file = "chart-9.csv"

    df = pd.read_csv(awarded_degrees_file)
    rows = df.iloc[14:89]
    degrees = {}

    degree_dist = {}
    for index, row in rows.iterrows():
        if row['Classified first degree qualifications by class'] in degrees:
            degrees[row['Classified first degree qualifications by class']] += float(row['Unnamed: 2'])
        else:
            degrees[row['Classified first degree qualifications by class']] = float(row['Unnamed: 2'])

    denom = sum(degrees.values())
    for _ in degrees:
        degree_dist[_] = degrees[_] / denom

    degree_types = list(degree_dist.keys())
    probabilities = list(degree_dist.values())
    return degree_types, probabilities

degree_types, probabilities = grades_dist()


def uni_ranking_dist():
    '''
    Returns a distribution that will be used to
    decide which university a graduate attended
    '''
    davides_filth = 'dt051-table-49.csv'
    df = pd.read_csv(davides_filth)
    uni_dict = {}

    for uni in df['Institution']:
        try:
            match = process.extractOne(uni,df['HE provider'].dropna().unique(),scorer=fuzz.token_sort_ratio)
            matched_uni = match[0]
            row = df.loc[df['HE provider'] == matched_uni]
            uni_dict[uni] = row['STEM total'].iloc[0]
        except:
            continue

    universities = list(uni_dict.keys())
    uni_list = list(uni_dict.keys())
    return universities, uni_list, uni_dict


universities, uni_list, uni_dict = uni_ranking_dist()
print(uni_dict)
grade_ranges = {
    'First class honours': [70, 100],
    'Upper second class honours': [60, 70],
    'Lower second class honours': [50, 60],
    'Third class honours/Pass': [40, 50]
}


def initialise_graduate_population(grad_num=100):
    graduates = []
    for i in range(grad_num):
        graduates.append(Graduate(i))
    return graduates


def initialise_employer_population(emp_num=100):
    employers = []
    for i in range(emp_num):
        employers.append(Employer(i))
    return employers


class Graduate():
    def __init__(self, index):
        self.index = index
        self.n_internships = 0
        self.assign_grade()
        rank_norm = self.assign_rank()
        self.employed = False

        self.w_2 = 0.5  # change constants later
        self.w_1 = 0.75
        self.w_s = 1
        self.w_e = 0.5
        self.t = 0.7
        self.n = 0.96
        self.scale = 50

        grade_norm = self.uni_grade / 100

        # Suitability score, Employability score, Intership score and Total score
        self.S = (self.w_1 * grade_norm + self.w_2 * rank_norm) / (self.w_1 + self.w_2)
        self.E = self.scale*abs(abs(self.t - grade_norm)**self.n - np.arctan(abs(self.t - grade_norm))**self.n)
        self.C = np.log(1 + self.n_internships)
        self.T = (self.w_s * self.S - self.w_e * self.E) / (self.w_e + self.w_s)


    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))


    def assign_grade(self):
        uni_class = np.random.choice(degree_types,p=probabilities)
        self.uni_grade = np.random.randint(
            grade_ranges[uni_class][0],
            grade_ranges[uni_class][1]
        ) # normalising

    def assign_rank(self):
        uni = np.random.choice(universities, size=1, p=list(uni_dict.values())/sum(uni_dict.values()))
        self.uni_ranking = uni_list.index(uni)
        self.uni = uni
        return 1 - uni_list.index(uni) / len(uni_list)

    def application_process_poocas(self, employers):
        w_oa = 0.5
        w_p = 0.7
        popularities = np.array([e.popularity for e in employers])
        number_of_applicants = np.array([len(e.applicants)/len(employers) for e in employers])
        choices = []
        risk_score = self.S + 0.1
        target_scores = np.random.uniform(0, risk_score, 5)
        for target in target_scores:
            idx = np.argmin((np.abs(popularities - (target + np.random.uniform(-0.15, 0.05))) + number_of_applicants) / (w_oa + w_p))
            choices.append(employers[idx])
        for company in choices:
            company.applicants.append(self.index)

    def application_process_normal(self, employers):
        applications = random.sample(employers, round(0.5*len(employers))) # just picking random companies at the moment
        for employer in applications:
            employer.applicants.append(self.index)



class Employer():
    def __init__(self, index):
        self.index = index
        self.ability_threshold = np.random.randint(0, 1)  # not random, choose another dist later
        self.popularity = np.random.randint(0, 100) / 100  # not random, choose another dist later
        self.c = 0.5
        self.l = self.c * np.exp(self.popularity)
        self.applicants = []
        self.employees = []
        self.vacancies = 5

    def hiring(self, graduates):
        new_employees = []
        self.applicants.sort(key=lambda i: graduates[i].T)

        for idx in self.applicants:
            if not graduates[idx].employed:
                new_employees.append(idx)
                graduates[idx].employed = True

            if len(new_employees) >= self.vacancies:
                break

        self.employees.extend(new_employees)


