import numpy as np
import math
import pandas as pd
from rapidfuzz import process, fuzz
import streamlit as st

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
            uni_dict[uni] = -row['STEM total'].iloc[0]
        except:
            continue

    universities = list(uni_dict.keys())
    uni_list = list(uni_dict.keys())
    return universities, uni_list, uni_dict

universities, uni_list, uni_dict = uni_ranking_dist()

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
        popularities = np.array([e.popularity for e in employers])
        risk_choice = np.argmin(np.abs(popularities - (self.S + 0.1)))
        safety_choice = np.argmin(np.abs(popularities - (self.S - 0.1)))
        other_choices = np.argsort(np.abs(popularities - (self.S - 0.1)))[:3]
        risk_choice.applicants.append(self.index)
        safety_choice.applicants.append(self.index)
        for choice in other_choices:
            choice.applicants.append(self.index)


class Employer():
    def __init__(self, index):
        self.index = index
        self.ability_threshold = np.random.randint(0, 1)  # not random, choose another dist later
        self.popularity = np.random.randint(0, 100) / 100  # not random, choose another dist later
        self.c = 0.5
        self.l = self.c * np.exp(self.popularity)
        self.applicants = []


################## STREAMLIT #####################

st.set_page_config(
    page_title="Graduate Employment Simulation",
    layout="wide"
)

st.title("Graduate Employment Simulation")

st.write(
    "Simulate graduate and employer populations "
    "and examine the resulting employment outcomes."
)

st.sidebar.header("Simulation Parameters")

grad_num = st.sidebar.number_input(
    "Number of graduates",
    min_value=1,
    max_value=100000,
    value=1000,
    step=100
)

emp_num = st.sidebar.number_input(
    "Number of employers",
    min_value=1,
    max_value=10000,
    value=100,
    step=10
)

if st.sidebar.button("Run simulation"):

    graduates = initialise_graduate_population(grad_num)
    employers = initialise_employer_population(emp_num)

    st.session_state["graduates"] = graduates
    st.session_state["employers"] = employers

    st.success("Simulation completed.")



if "graduates" in st.session_state:

    graduates = st.session_state["graduates"]
    employers = st.session_state["employers"]

    st.divider()

    st.subheader("Population")

    col1, col2 = st.columns(2)

    col1.metric(
        "Number of graduates",
        len(graduates)
    )

    col2.metric(
        "Number of employers",
        len(employers)
    )

    st.divider()

    st.subheader("Graduate characteristics")

    graduate_data = pd.DataFrame([
        {
            "University": g.uni,
            "Grade": g.uni_grade,
            "University ranking": g.uni_ranking,
            "Internships": g.n_internships,
            "Suitability score": g.S,
            "Total score": g.T
        }
        for g in graduates
    ])

    col1, col2 = st.columns(2)

    with col1:
        st.write("Grade distribution")
        st.bar_chart(
            graduate_data["Grade"].value_counts(bins=10).sort_index().rename(
                index=lambda x: f"{int(x.left)} - {int(x.right)}"
            ),
            x_label="Grade range",
            y_label="Number of graduates"
        )

    with col2:
        st.write("University distribution")
        st.bar_chart(
            graduate_data["University"].value_counts().head(15)
        )

    st.subheader("Graduate data")

    st.dataframe(
        graduate_data,
        use_container_width=True
    )

    st.download_button(
        "Download graduate data",
        graduate_data.to_csv(index=False),
        "graduate_data.csv",
        "text/csv"
    )

