"""
Name: John-Michael Garofano
CS230: Section SN5
Data: Post-Secondary School Locations
URL:

Description:

This program is used to interpret data based on Universities across the U.S. and its territories. The data includes
location (latitude and longitude) as well as statistical identifiers. The heatmap is used to visualize the significance
of each area based on the area's density of universities for the selected statistical entity. The chart is used to
display the frequency of each code for the selected entity within the selected state. A regular map is located at
the end for reference, along with the data and short descriptions of each statistical entity.

"""

#Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pydeck as pdk
import mapbox as mb



#These are used for reference later on

COLORS = {'Red': 'pink',
          'Green': 'lightgreen',
          'Blue': 'lightblue',
          'Purple': 'magenta',
          }

STATISTICAL_QUERIES = ['LOCALE', 'CBSA', 'CSA', 'NECTA', 'CD', 'SLDL', 'SLDU']


#The Get Data function is used to read the csv file and returns the data frame
def get_data():

    file='Postsecondary_School_Locations_-_Current.csv'
    data = pd.read_csv(file)
    df = pd.DataFrame(data)

    return df


#This function creates the heatmap
def heatmap(df, scheme, column):

    st.subheader("Heatmap")
    df = df[df[column] != 'N']
    df = df[['lon', 'lat']]
    weight = 0.5

#This if loop uses RBG color codes to set the color scale for the visuals based on the selected scheme
    if scheme == 'Red':
        c1 = [255,123,123]
        c2 = [255,83,83]
        c3 = [255,42,42]
        c4 = [255,0,0]
    elif scheme == 'Green':
        c1 = [155,232,155]
        c2 = [96,179,96]
        c3 = [36,134,36]
        c4 = [0,128,0]
    elif scheme == 'Blue':
        c1 = [123,149,255]
        c2 = [85,119,255]
        c3 = [44,86,255]
        c4 = [0,0,255]
    else:
        c1 = [239,183,255]
        c2 = [220,102,255]
        c3 = [233,158,255]
        c4 = [196,0,255]

    scale = [
        c1,
        c2,
        c3,
        c4
    ]

#View State sets the default map view
    view_state = pdk.ViewState(
    latitude=df["lat"].mean(),
    longitude=df["lon"].mean(),
    zoom=1,
    pitch=0.5
    )

#Universities is the layer that gets placed over the map
    universities = pdk.Layer(
        "HeatmapLayer",
        data=df,
        opacity=3,
        get_position=["lon", "lat"],
        aggregation=pdk.types.String("MEAN"),
        color_range=scale,
        threshold=0.1,
        get_weight=weight,
        pickable=True,
    )

#The deck uses its parameters to adjust the map settings
    hmap = pdk.Deck(
        layers=[universities],
        map_provider="mapbox",
        initial_view_state=view_state,
        map_style=pdk.map_styles.LIGHT,
        tooltip={"text": "Darker areas have a higher density of universities."},
    )

#creates the actual map
    st.pydeck_chart(hmap)


#The Freq Graph function is the core function of the bar chart and returns the plot
def freq_graph(df, scheme, curstate, column):

#This code block creates a smaller dataframe, taking each record from the main dataframe that matches the selected area.
#After, it adds each unique code within that area to a new list.
    st.subheader("\nFrequency Plot by Area")
    newdf = df[df['STATE'] == curstate]
    data = newdf[column].sort_values(ascending=True)
    unique_data = []
    for i in data:
        if i not in unique_data:
            unique_data.append(i)
        else:
            continue

#This block uses that list to find the frequency of each code within the selected area and adds it to a dictionary
    freq_dict = {}
    temp_list = []
    for item in unique_data:
       count = 0
       for index, row in newdf.iterrows():
           if row[column] == item:
               count += 1
           else:
               continue
       temp_list.append(count)
       freq_dict[curstate] = temp_list

#This block creates the bar graph based on the frequency of each code within the area
    x = range(len(unique_data))
    y = freq_dict[curstate]
    fig, ax = plt.subplots()
    plt.xticks(range(0,len(unique_data)),unique_data, rotation=60)
    ax.grid(color='lightgrey', linestyle='-',linewidth=0.5, zorder=0)
    ax.set_title(f'Displaying frequency of {column} codes in {curstate}')
    ax.set_xlabel("Identifier Codes")
    ax.set_ylabel("Code Frequency")
    ax.margins(0.05,0.05)
    ax.bar(x, y, color=scheme, width=1, zorder=3)

    return plt


#The worldmap function is used to create the map of actual locations of each university
def worldmap(df, scheme):

#This code block uses the scheme to set the maps colors
    st.subheader("\nUniversities on the Map")
    if scheme == 'Red':
        tcolor = 'pink'
        pcolor = [139,0,0]
    elif scheme == 'Green':
        tcolor = 'lightgreen'
        pcolor = [0,128,0]
    elif scheme == 'Blue':
        tcolor = 'lightblue'
        pcolor = [0,0,255]
    else:
        tcolor = 'thistle'
        pcolor = [128,0,128]

#Same as the heatmap, this sets the default view
    view_state = pdk.ViewState(
    latitude=df["lat"].mean(),
    longitude=df["lon"].mean(),
    zoom=1,
    pitch=0.5
    )

#This sets the layer to be placed on top of the map
    layer1 = pdk.Layer('ScatterplotLayer',
                  data=df,
                  get_position='[lon, lat]',
                  get_radius= 'scaled_radius',
                  radius_scale = 2,
                  radius_min_pixels= 5,
                  radius_max_pixels = 15,
                  get_color=pcolor,
                  pickable=True
                  )

#This block sets the tooltip to the respective university
    tool_tip = {"html": "NAME:<br/> <b>{NAME}</b> ",
            "style": { "backgroundColor": tcolor,
                        "color": "white"}
          }

#This creates the map settings
    map = pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=view_state,
    layers=[layer1],
    tooltip= tool_tip
    )

#This actually creates the map
    st.pydeck_chart(map)


#The main function calls the above functions
#It wraps everything together and creates the streamlit site
def main():

    df = get_data()
    df = df.rename(columns={'LAT': 'lat'})
    df = df.rename(columns={'LON': 'lon'})

    st.title("Final Project - University Locations")
    st.write("This program is used to interpret data based on universities across the U.S. and its territories. The data"
             " includes location (latitude and longitude) as well as each universities' statistical identifiers. The heatmap is used to "
             "visualize the significance of each area based on the area's density of universities for the selected "
             "statistical entity. The chart is used to display the frequency of universities with each identifier under the selected entity within"
             " the selected state. A fixed map showing the location of each university is located at the end for reference, along with the data and short "
             "descriptions of each statistical entity. Note that some codes are region specific, such as NECTA, "
             "which only covers the New England area.")
    st.header("Visuals")

    states = df['STATE'].sort_values(ascending=True)
    states_list = []
    for i in states:
        if i not in states_list:
            states_list.append(i)
        else:
            continue

    curstate = st.sidebar.selectbox("Select an area: ", states_list)
    column = st.sidebar.selectbox('Select a statistical query: ', STATISTICAL_QUERIES)
    scheme = st.sidebar.radio("Select a color scheme: ", list(COLORS.keys()))

    st.pyplot(freq_graph(df, scheme, curstate, column))
    st.write("*Universities with code 'N' are not identified under the selected query. ")
    st.write("This chart displays how many universities use different codes under the selected statistical query within "
             "the selected area.")
    heatmap(df, scheme, column)
    st.write('This heatmap visualizes the proportional weight each region has on the given statistical query.')
    worldmap(df, scheme)
    st.write('This map is shown to compare the weight of different regions with actual locations of universities around '
             'the country.')
    st.subheader("The data ")
    st.dataframe(df)

    st.subheader("Definitions")
    st.write(f"LOCALE: The NCES locale framework was designed to provide a general indicator of the type of geographic area where a school is located. [source](https://nces.ed.gov/programs/edge/docs/NCES_LOCALE_USERSMANUAL_2016012.pdf) \n"
             "\nCBSA: A Core Based Statistical Area (CBSA) consists of a U.S. county or counties or equivalent entities associated with at least one core (urbanized area or urban cluster) with a population of at least 10,000 along with any adjacent counties having a high degree of social and economic integration with the core as measured through commuting ties with the counties containing the core. [source](https://earthworks.stanford.edu/catalog/stanford-dy982nn7286)\n"
             "\nCSA: A geographic entity consisting of two or more adjacent Core Based Statistical Areas with employment interchange measures of at least 15. [source](https://www.federalregister.gov/documents/2021/07/16/2021-15159/2020-standards-for-delineating-core-based-statistical-areas)\n"
             "\nNECTA: An alternative set of geographic entities, similar in concept to the county-based core based statistical areas (CBSAs) delineated nationwide, that the Office of Management and Budget delineates in New England based on county subdivisions???usually cities and towns. NECTAs are delineated using the same criteria as county-based CBSAs, and, similar to CBSAs, NECTAs are categorized as metropolitan or micropolitan. [source](https://www.census.gov/programs-surveys/metro-micro/about/glossary.html)\n"
             "\nCD: Census divisions are groupings of states that are subdivisions of the four census regions. [source](https://www.easidemographics.com/mdbhelp/html/census_division_1.htm)\n"
             "\nSLDL & SLDU: State legislative districts are the areas from which members are elected to state or equivalent entity legislatures. State legislative districts embody the upper (senate???SLDU) and lower (house???SLDL) chambers of the state legislatures for all 50 states, the District of Columbia, and Puerto Rico. [source](https://nces.ed.gov/programs/edge/docs/EDGE_GEOCODE_POSTSEC_FILEDOC.pdf)")

main()


#REFERENCES

#Matplotlib.org
#PyPi.org/project/pydeck
#StackOverflow
#https://rgbcolorcode.com/color/converter/
