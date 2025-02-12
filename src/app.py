#!/usr/bin/env python

"""
To run, paste into terminal: streamlit run seedcount.py
"""

import streamlit as st
import pandas as pd
from processing import SeedData, Stats
from plotting import generate_plots


# @st.cache()
def load_data_once():
    """ only load the data once and cache it """
    return SeedData()


def write_header():
    """ write the title and instructions """
    st.title("Seed Count")
    st.write((
        "Please begin by selecting your soil moisture level "
        "and desired species from the sidebar to the left."
    ))


# @st.cache(suppress_st_warning=True)
def sidebar_moisture_selector(data):
    """ a selector of the moisture type """
    moisture_value = st.sidebar.selectbox(
        "Choose a soil moisture level", 
        ('ALL', 'Dry to Average Soil', 'Consistently Moist Soil', 'Saturated Soil'),
    )

    # resets .subdata selection from .data
    if moisture_value != "ALL":
        data.subdata = data.data[data.data.habitat == moisture_value].copy()
    else:
        data.subdata = data.data.copy()


def display_seeds(data):
    """
    create 
    """
    # create input for each spp in subdata
    usrchoices = {}
    for spp in data.subdata.index:

        # get common name of this spp
        common_name = data.subdata.at[spp, "common_name"]

        # create a number input
        count = st.sidebar.number_input(
            f"{spp}  ({common_name})",
            min_value=0, 
            max_value=500, 
            step=1,
        )
        if count:
            usrchoices[spp] = count

    # convert dict to df for displaying as a table
    usrchoicesdf = pd.DataFrame.from_dict(
        usrchoices, 
        orient="index", 
        columns=["plants_per_meter"],
    )

    # display
    if usrchoicesdf.size:
        st.write("#### You selected:")
        st.table(usrchoicesdf)

    # subselect these plants from dataset
    data.subdata = data.subdata.loc[usrchoicesdf.index, :]
    data.subdata = pd.concat([data.subdata, usrchoicesdf], axis=1)


def display_warnings(data, stats):
    """
    Show warnings in warning boxes
    """
    if data.subdata.fall.sum() > 0:
        st.warning((
            "**Cold Stratification Required**: Some species on your list "
            "require cold stratification. Fall planting recommended to "
            "reduce dormancy and improve establishment."
        ))

    forbs_density = data.subdata[data.subdata.forb == 1].plants_per_meter.sum()
    all_density = data.subdata.plants_per_meter.sum()
    if forbs_density / all_density > 0.6:
        st.warning((
            "**Forb Density is High**: Consider adding more grasses or "
            "sedges to improve weed suppression and prevent erosion, "
            "especially if your site is sloped."
        ))

    if stats.data.seeds_per_meter.sum() < 400.0: 
        st.warning(
            "Consider increasing number of plants for better weed "
            "suppression and erosion control."
        )

    if stats.data.seeds_per_meter.sum() > 1200.0:
        st.warning(
            "Consider decreasing desired density of plants to maintain "
            "diversity."
        )


def display_purchase_info(stats):
    """
    show table and info boxes
    """
    st.write("### Purchase List")
    st.table(stats.purchaselist.sort_index())
    st.info(
        "The seeding rate of your mix is **{:.2f} pounds per acre**."
        .format(stats.data.pounds_per_acre.sum())
    )
    st.info(
        "Seed with an equal volume of bulking agent, such as kitty "
        "litter, and an appropiate nurse crop from the list below."
    )
    st.write("### Here is a visualization of your desired species density:")


def display_plot(data, stats):
    """
    Create plots from function in plotting module
    TODO: more on this...
    """
    # altchart = generate_plots(data, stats)
    # st.altchart(altchart)



if __name__ == "__main__":
    
    # load the data once.
    data = load_data_once()

    # Title and instructions
    write_header()

    # OPTION: Sidebar for selecting soil moisture level
    sidebar_moisture_selector(data)

    # Display selected plants
    display_seeds(data)

    # calculate Stats    
    stats = Stats(data)

    # only do this latter stuff if some selections were made
    if stats.data.size:

        # Display warnings
        display_warnings(data, stats)

        # Display purchase list info
        display_purchase_info(stats)

        # display plots
        # display_plots(data, stats)
