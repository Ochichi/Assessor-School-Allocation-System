from supabase_connection import supabase


def create_tables():
    """
    Tables are created in Supabase SQL Editor.
    This function remains so app.py does not need changes.
    """
    pass



def save_allocation(vvid, name, date, school):

    response = supabase.table("allocations").insert(
        {
            "vvid": vvid,
            "assessor_name": name,
            "testing_date": date,
            "school_name": school
        }
    ).execute()

    return response



def check_existing_allocation(vvid, date):

    response = (
        supabase
        .table("allocations")
        .select("*")
        .eq("vvid", vvid)
        .eq("testing_date", date)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None



def check_school_capacity(date, school, required):

    response = (
        supabase
        .table("allocations")
        .select("id")
        .eq("testing_date", date)
        .eq("school_name", school)
        .execute()
    )

    current_allocations = len(response.data)

    return current_allocations < required



def get_available_schools(date, schedule):

    available_schools = []


    for _, row in schedule.iterrows():

        if row["Testing Date"] == date:

            school = row["School Name"]

            required = row["Required Assessors"]


            response = (
                supabase
                .table("allocations")
                .select("id")
                .eq("testing_date", date)
                .eq("school_name", school)
                .execute()
            )


            allocated = len(response.data)


            remaining = required - allocated


            if remaining > 0:

                available_schools.append(
                    {
                        "School Name": school,
                        "Available Slots": remaining
                    }
                )


    return available_schools