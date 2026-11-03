import numpy as np
import scipy

t = 70
#Version Control test 03/11

class Graduate():
    def __init__(self, t):
        self.uni_grade = np.random.randint(1, 100) # not random, choose another dist later
        self.uni_ranking = np.random.randint(1, 164) # not random, choose another dist later
        self.w_2 = 0.5   # change constants later
        self.w_1 = 0.5
        self.w_s = 0.5
        self.w_e = 0.5

        self.s = self.w_1*self.uni_grade + self.w_2*self.uni_ranking # suitability score 
        self.e = self.w_e * np.linalg.norm(t - self.uni_grade) # employability score 
        self.c = self.sigmoid(self.w_s*self.s + self.w_e*self.e) # score between 0 and 1


    def sigmoid(x):
        return 1 / 1 + np.exp(-x)


class Employer():
    def __init__(self):
        self.ability_threshold = np.random.randint(0, 1) # not random, choose another dist later
        self.popularity = np.random.randint(0, 100) # not random, choose another dist later
        self.c = 0.5
        self.l = self.c*np.exp(self.popularity) # use softmax later to make a probability dist
        






    
    