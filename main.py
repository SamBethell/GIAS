from unemployment import Employer, Graduate, initialise_graduate_population, initialise_employer_population
import streamlit as st
import pandas as pd






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
