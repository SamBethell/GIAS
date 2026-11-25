import streamlit as st
import pandas as pd
import random

from unemployment import (
    Employer,
    Graduate,
    initialise_employer_population
)

st.set_page_config(
    page_title="Graduate Employment Simulation",
    layout="wide"
)

st.title("Graduate Employment Simulation")

st.sidebar.header("Simulation Parameters")

grad_num = st.sidebar.number_input(
    "Number of graduates",
    min_value=1,
    value=1000
)

emp_num = st.sidebar.number_input(
    "Number of employers",
    min_value=1,
    value=100
)


def average_T(employer, graduates):
    """
    Mean T score of the graduates an employer hired.
    Returns None if the employer hired nobody.
    """
    if not employer.employees:
        return None
    scores = [graduates[i].T for i in employer.employees]
    return sum(scores) / len(scores)


def employer_table(employers, graduates):
    """
    Builds the per-employer results table, including the
    average T score of each employer's employees.
    """
    return pd.DataFrame([
        {
            "Employer": employer.index,
            "Vacancies": employer.vacancies,
            "Applicants": len(employer.applicants),
            "Employees": len(employer.employees),
            "Average suitability of Employees": average_T(employer, graduates)
        }
        for employer in employers
    ])


def run_simulation(application_method, progress_bar, offset, share, label):
    """
    offset: where this simulation's share of the bar starts (0-1)
    share:  how much of the bar this simulation covers (0-1)
    """
    # steps: create graduates, graduates apply, employers hire
    total_steps = 2 * grad_num + emp_num
    update_every = max(1, total_steps // 100)  # avoid updating the UI every step
    done = 0

    def tick(text):
        nonlocal done
        done += 1
        if done % update_every == 0 or done == total_steps:
            fraction = min(1.0, offset + share * done / total_steps)
            progress_bar.progress(fraction, text=text)

    # Initialise independent populations
    graduates = []
    for i in range(grad_num):
        graduates.append(Graduate(i))
        tick(f"{label}: creating graduates")

    employers = initialise_employer_population(emp_num)

    # Graduates submit applications using the selected scheme
    for graduate in graduates:
        if application_method == "normal":
            graduate.application_process_normal(employers)

        elif application_method == "gias":
            graduate.application_process_gias(employers)
        tick(f"{label}: submitting applications")

    # Randomise employer hiring order
    random.shuffle(employers)

    # Employers process their applicants
    for employer in employers:
        employer.hiring(graduates)
        tick(f"{label}: employers hiring")

    return graduates, employers


if st.sidebar.button("Run simulation"):

    progress_bar = st.progress(0.0, text="Starting simulation...")

    # Run both schemes independently, each taking half of the bar
    normal_graduates, normal_employers = run_simulation(
        "normal", progress_bar, offset=0.0, share=0.5, label="Normal"
    )

    gias_graduates, gias_employers = run_simulation(
        "gias", progress_bar, offset=0.5, share=0.5, label="Gias"
    )

    progress_bar.progress(1.0, text="Done")
    progress_bar.empty()  # remove the bar once finished (delete to keep it visible)

    # Store results
    st.session_state["normal_graduates"] = normal_graduates
    st.session_state["normal_employers"] = normal_employers

    st.session_state["gias_graduates"] = gias_graduates
    st.session_state["gias_employers"] = gias_employers

    st.success("Both simulations completed!")


if "normal_graduates" in st.session_state:

    schemes = {
        "Normal": (
            st.session_state["normal_graduates"],
            st.session_state["normal_employers"]
        ),
        "Gias": (
            st.session_state["gias_graduates"],
            st.session_state["gias_employers"]
        )
    }

    results = {}

    # Calculate statistics for each scheme
    for scheme, (graduates, employers) in schemes.items():

        employed_count = sum(
            graduate.employed for graduate in graduates
        )

        total_vacancies = sum(
            employer.vacancies for employer in employers
        )

        filled_vacancies = sum(
            len(employer.employees) for employer in employers
        )

        total_applications = sum(
            len(employer.applicants) for employer in employers
        )

        employment_rate = employed_count / len(graduates) * 100

        vacancy_fill_rate = (
            filled_vacancies / total_vacancies * 100
            if total_vacancies > 0 else 0
        )

        results[scheme] = {
            "Graduates": len(graduates),
            "Employed": employed_count,
            "Unemployed": len(graduates) - employed_count,
            "Employment Rate (%)": employment_rate,
            "Total Vacancies": total_vacancies,
            "Filled Vacancies": filled_vacancies,
            "Vacancy Fill Rate (%)": vacancy_fill_rate,
            "Total Applications": total_applications,
            "Average Applications per Graduate": (
                total_applications / len(graduates)
            )
        }

    # Comparison table
    st.subheader("Scheme Comparison")

    comparison = pd.DataFrame(results).T

    st.dataframe(
        comparison.style.format({
            "Employment Rate (%)": "{:.2f}%",
            "Vacancy Fill Rate (%)": "{:.2f}%",
            "Average Applications per Graduate": "{:.2f}"
        }),
        use_container_width=True
    )

    # Employment rate comparison
    st.subheader("Employment Rate")

    col1, col2 = st.columns(2)

    col1.metric(
        "Normal Scheme",
        f"{results['Normal']['Employment Rate (%)']:.2f}%"
    )

    col2.metric(
        "Gias Scheme",
        f"{results['Gias']['Employment Rate (%)']:.2f}%",
        delta=(
            f"{results['Gias']['Employment Rate (%)'] - results['Normal']['Employment Rate (%)']:.2f} "
            "percentage points"
        )
    )

    # Employer-level results (includes average T of each employer's employees)
    st.subheader("Employer Results")

    tab1, tab2 = st.tabs(["Normal", "Gias"])

    with tab1:
        normal_data = employer_table(
            st.session_state["normal_employers"],
            st.session_state["normal_graduates"]
        )
        st.dataframe(
            normal_data.style.format({"Average T of Employees": "{:.4f}"}, na_rep="-"),
            use_container_width=True
        )

    with tab2:
        gias_data = employer_table(
            st.session_state["gias_employers"],
            st.session_state["gias_graduates"]
        )
        st.dataframe(
            gias_data.style.format({"Average T of Employees": "{:.4f}"}, na_rep="-"),
            use_container_width=True
        )

    # Graduate-level results
    st.subheader("Graduate Results")

    tab1, tab2 = st.tabs(["Normal", "Gias"])

    with tab1:
        normal_graduate_data = pd.DataFrame([
            {
                "Graduate": graduate.index,
                "Employed": graduate.employed,
                "Suitability": graduate.T
            }
            for graduate in st.session_state["normal_graduates"]
        ])

        st.dataframe(normal_graduate_data, use_container_width=True)

    with tab2:
        gias_graduate_data = pd.DataFrame([
            {
                "Graduate": graduate.index,
                "Employed": graduate.employed,
                "T": graduate.T
            }
            for graduate in st.session_state["gias_graduates"]
        ])

        st.dataframe(gias_graduate_data, use_container_width=True)