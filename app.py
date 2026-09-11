import streamlit as st
import pandas as pd

from database import (
    create_tables,
    save_allocation,
    check_existing_allocation,
    check_school_capacity,
    get_available_schools
)

from supabase_connection import supabase


# Create database tables
create_tables()


# Page title
import streamlit as st

st.set_page_config(
    page_title="Assessor Allocation System",
    page_icon="📋",
    layout="centered"
)
st.title("Assessor School Allocation System")

st.info("""
Welcome to the Assessor School Allocation System.

Use your VVID to log in and select your testing assignment.

Allocations are confirmed on a first-come basis.
""")

# Load data files

assessors = pd.read_csv(
    "data/assessors.csv"
)

schedule = pd.read_csv(
    "data/testing_schedule.csv"
)


# =========================
# LOGIN SECTION
# =========================

st.subheader("Assessor Login")

vvid = st.text_input("Enter VVID")


if st.button("Login"):

    assessor = assessors[
        assessors["VVID"].astype(str).str.strip()
        ==
        str(vvid).strip()
    ]


    if not assessor.empty:

        st.session_state.logged = True
        st.session_state.vvid = str(vvid).strip()
        st.session_state.name = assessor.iloc[0]["Name"]

        st.success(
            f"Welcome {st.session_state.name}"
        )


    else:

        st.error(
            "Invalid VVID"
        )


# =========================
# ALLOCATION SECTION
# =========================

if st.session_state.get("logged"):


    st.divider()

    st.subheader(
        "Select Testing Date"
    )


    dates = schedule[
        "Testing Date"
    ].unique()


    selected_date = st.selectbox(
        "Testing Date",
        dates
    )


    # Check existing allocation

    existing = check_existing_allocation(
        st.session_state.vvid,
        selected_date
    )


    if existing:

        st.warning(
            "You already have an allocation on this date."
        )


    else:


        available_schools = get_available_schools(
            selected_date,
            schedule
        )


        if len(available_schools) == 0:

            st.warning(
                "No schools available on this date."
            )


        else:


            school_options = [
                f"{x['School Name']} ({x['Available Slots']} slots available)"
                for x in available_schools
            ]


            selected_school_display = st.selectbox(
                "Select School",
                school_options
            )


            school = selected_school_display.split(" (")[0]


            if st.button("Confirm Allocation"):


                required = schedule[
                    (schedule["Testing Date"] == selected_date)
                    &
                    (schedule["School Name"] == school)
                ]["Required Assessors"].iloc[0]


                available = check_school_capacity(
                    selected_date,
                    school,
                    required
                )


                if available:


                    save_allocation(
                        st.session_state.vvid,
                        st.session_state.name,
                        selected_date,
                        school
                    )


                    st.success(
                        "Allocation successful"
                    )


                    st.rerun()


                else:

                    st.error(
                        f"{school} is already full. Please select another school."
                    )


# =========================
# ALLOCATION REPORT
# =========================

st.divider()

st.subheader(
    "Allocation Report"
)


response = (
    supabase
    .table("allocations")
    .select("*")
    .execute()
)


allocations = pd.DataFrame(
    response.data
)


st.dataframe(
    allocations
)
