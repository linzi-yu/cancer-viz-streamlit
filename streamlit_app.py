import altair as alt
import pandas as pd
import streamlit as st

### P1.2 ###

@st.cache
def load_data():
    cancer_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/cancer_ICD10.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Cancer", "Sex"],
        var_name="Age",
        value_name="Deaths",
    )

    pop_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/population.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Sex"],
        var_name="Age",
        value_name="Pop",
    )

    df = pd.merge(left=cancer_df, right=pop_df, how="left")
    df["Pop"] = df.groupby(["Country", "Sex", "Age"])["Pop"].fillna(method="bfill")
    df.dropna(inplace=True)

    df = df.groupby(["Country", "Year", "Cancer", "Age", "Sex"]).sum().reset_index()
    df["Rate"] = df["Deaths"] / df["Pop"] * 100_000
    return df

df = load_data()

st.write("## Age-specific cancer mortality rates")

### P2.1 ###
min_value=min(df['Year'])
max_value=max(df['Year'])
year = st.slider( "Year", min_value, max_value, 2012)
# st.slider( "Year", 1994, 2020, 2012)

# year = st.slider( "Year", 1994, 2020, 2012)
subset = df[df["Year"] == year]
### P2.1 ###


### P2.2 ###
# replace with st.radio
# sex = "M"
sex = st.radio(
     "Sex",
     ('M', 'F'))
subset = subset[subset["Sex"] == sex]
### P2.2 ###


### P2.3 ###
# replace with st.multiselect
# (hint: can use current hard-coded values below as as `default` for selector)
countries = st.multiselect(
     'Countries',
     df["Country"].unique(),
     [
    "Austria",
    "Germany",
    "Iceland",
    "Spain",
    "Sweden",
    "Thailand",
    "Turkey",
])


subset = subset[subset["Country"].isin(countries)]
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
cancer = st.selectbox(
     'Cancer',
     (df["Cancer"].unique()))
subset = subset[subset["Cancer"] == cancer]
### P2.4 ###


### P2.5 ###
ages = [
    "Age <5",
    "Age 5-14",
    "Age 15-24",
    "Age 25-34",
    "Age 35-44",
    "Age 45-54",
    "Age 55-64",
    "Age >64",
]
#select an age group
# create an altair selector for age selection
age_selection = alt.selection_single(
    fields=['Age']
)
base = alt.Chart(subset)

chart = base.mark_rect().encode(
    x=alt.X("Age", sort=ages),
    y=alt.Y("Country"),
    color=alt.Color("Rate:Q", title = "Mortality rate per 100k", scale=alt.Scale(type='log', domain=(0.01, 1000), clamp=True)),
    tooltip=["Rate"],
    opacity=alt.condition(age_selection, alt.value(1), alt.value(0.2))
).add_selection(
    #add the altair selector to the heatmap scale
    age_selection
).properties(
    width=440,
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
)
### P2.5 ###

# st.altair_chart(chart, use_container_width=True)


bar_chart = base.mark_bar().encode(
    x=alt.X("Pop:Q", stack=True, title = "Population"),
    y=alt.Y("Country"),
    tooltip=["Age","Pop"],
).transform_filter(
     #update donut chart based on scale selector in heatmap
    age_selection
).properties(
    width=440,
    title=f"Population size of each country for {'males' if sex == 'M' else 'females'} in {year}",
)

bonus_chart = alt.vconcat(chart, bar_chart)
st.altair_chart(bonus_chart, use_container_width=True)

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")
