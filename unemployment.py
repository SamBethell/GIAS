import numpy as np
import scipy
import math


def initialise_graduate_population(grad_num=100):
    graduates = []
    for i in range(grad_num):
        graduates.append(Graduate())


def initialise_employer_population(emp_num=100):
    employers = []
    for i in range(emp_num):
        employers.append(Employer())


class Graduate():
    def __init__(self):
        self.n_internships = 0
        self.uni_grade = np.random.randint(1, 100)  # not random, choose another dist later
        self.uni_ranking = np.random.randint(1, 164)  # not random, choose another dist later

        self.w_2 = 0.5  # change constants later
        self.w_1 = 0.5
        self.w_s = 0.5
        self.w_e = 0.5
        self.t = 70
        self.n = 4

        # Suitability score, Employability score, Intership score and Total score
        self.S = self.w_1 * self.uni_grade + self.w_2 * self.uni_ranking  # suitability score
        self.E = abs((self.t - self.uni_grade)**self.n - np.arctan(self.t - self.uni_grade))  # employability score
        self.C = np.log(1 + self.n_internships)
        self.T = self.w_s * self.S + self.w_e * self.E


    def sigmoid(self, x):
        return 1 / 1 + np.exp(-x)


class Employer():
    def __init__(self):
        self.ability_threshold = np.random.randint(0, 1)  # not random, choose another dist later
        self.popularity = np.random.randint(0, 100)  # not random, choose another dist later
        self.c = 0.5
        self.l = self.c * np.exp(self.popularity)  # use softmax later to make a probability dist
