import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import plotly.express as px

# Global constants
DATA_PATH = 'data/data_cache/'
CHICAGO_COORDINATES = [41.8781, -87.6298]
CHICAGO_BOUNDARIES_FILE = f'{DATA_PATH}chicago_boundaries.geojson'
DEFAULT_MAP_ZOOM = 10

# Enhanced caching functions for different data types
@st.cache_data
def load_csv(filepath):
    return pd.read_csv(filepath)

@st.cache_data
def load_parquet(filepath):
    return pd.read_parquet(filepath)

@st.cache_data
def load_json(filepath):
    return pd.read_json(filepath)

@st.cache_data
def load_data(filepath):
    """Generic data loading function that routes to appropriate loader based on file extension"""
    if filepath.endswith('.csv'):
        return load_csv(filepath)
    elif filepath.endswith('.parquet'):
        return load_parquet(filepath)
    elif filepath.endswith('.json'):
        return load_json(filepath)
    else:
        raise ValueError("Unsupported file format. Supported formats are CSV, Parquet, and JSON.")

@st.cache_data
def load_geojson():
    """Load and cache the Chicago boundaries GeoJSON file"""
    return gpd.read_file(CHICAGO_BOUNDARIES_FILE)

def create_choropleth_map(gdf, value_column, location=CHICAGO_COORDINATES, zoom=DEFAULT_MAP_ZOOM, 
                          color_scale='YlOrRd', legend_name=None):
    """Create a choropleth map from a GeoDataFrame with tooltip"""
    
    map_obj = folium.Map(location=location, zoom_start=zoom)
    
    choropleth = folium.Choropleth(
        geo_data=gdf.to_json(),
        name='choropleth',
        data=gdf,
        columns=['area_num_1', value_column],
        key_on='feature.properties.area_num_1',
        fill_color=color_scale,
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend_name or f'{value_column} by Community Area'
    ).add_to(map_obj)
    
    # Add tooltips
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            ['community' if 'community' in gdf.columns else 'Community Area', value_column], 
            aliases=['Community Area', value_column]
        )
    )
    
    return map_obj

def welcome():
    st.title("Analysis of Crime in Chicago")

    st.write("""
    In this project I will be using a publicly accessible [DATASET](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2/data) by the City of Chicago via the 
    [Chicago Data Portal](https://data.cityofchicago.org). The dataset contains over 8 million recorded crimes and is updated on a weekly basis. Due to the sheer amount of gun crime in Chicago, 
    they maintain a separate and comprehensive [DATASET](https://data.cityofchicago.org/Public-Safety/Violence-Reduction-Victims-of-Homicides-and-Non-Fa/gumc-mgzr/about_data) on shootings across the city, 
    seeing an average of one shooting per two hours. Since 2019 only seven days without a shooting have been recorded. 

    The main questions I sought to answer were:

    1. How has crime changed over the last 20 years?
    2. Why have narcotic crimes decreased over time despite high drug use?
    3. How is crime distributed across the city?
    4. How did Covid affect crime rates?
    5. What is the distribution of shootings?

    The majority of the pages on the left are interactive allowing you to explore the data yourself.
    """)

def plot_crime_types(df_bar_1):
    """Create bar chart of crime types"""
    pivot_bar1 = df_bar_1.pivot_table(index='Primary Type', values='count', aggfunc='sum')
    top_crimes1 = pivot_bar1.nlargest(35, 'count')

    fig_bar1, ax_bar1 = plt.subplots(figsize=(10, 6))
    top_crimes1.plot(kind='bar', ax=ax_bar1, color='skyblue')
    ax_bar1.set_title('Total Crime Counts by Type (Top 15)')
    ax_bar1.set_ylabel('Total Counts')
    ax_bar1.set_xlabel('Crime Type')
    ax_bar1.tick_params(axis='x', rotation=90)
    ax_bar1.grid(True)
    ax_bar1.legend(title='Crime Type', loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    
    return fig_bar1

def plot_crimes_by_hour(df_bar_2):
    """Create bar chart of crimes by hour"""
    pivot_bar2 = df_bar_2.pivot_table(index='Hour', values='Average', aggfunc='mean')

    fig_bar2, ax_bar2 = plt.subplots(figsize=(10, 6))
    pivot_bar2.plot(kind='bar', ax=ax_bar2, color='skyblue')
    ax_bar2.set_title('Average Crimes per Hour')
    ax_bar2.set_ylabel('Average Number of Crimes')
    ax_bar2.set_xlabel('Hour')
    ax_bar2.tick_params(axis='x', rotation=0)
    ax_bar2.grid(True)
    ax_bar2.legend(title='Average Crimes', loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    
    return fig_bar2

def plot_crime_trends(df_line_1, selected_types):
    """Create line graph of selected crime types over time"""
    filtered_data_line = df_line_1[df_line_1['Primary Type'].isin(selected_types)]
    pivot_data_line = filtered_data_line.pivot_table(index='Year', columns='Primary Type', values='Count', aggfunc='sum')

    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_data_line.plot(kind='line', ax=ax)
    ax.set_title('Top Crimes per Year by Committed Offense')
    ax.set_ylabel('Number of Crimes')
    ax.set_xlabel('Year')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True)
    ax.legend(title='Crime Type', loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    
    return fig

def crime_analysis():
    st.subheader('Overview of Crime in Chicago')

    # Key crime statistics
    st.info("""
    **Key Statistics:**
    - Average homicides per year: 534.0
    - Homicide rate: 19.8 per 100,000 inhabitants (based on population of 2,700,000)
    - Crime rate difference: 248.7% higher in non-tourist areas compared to tourist areas
    """)

    st.write('''
    This page serves as an overview of crime in Chicago and how it is distributed in terms of category and time.
    ''')

    # Load Data
    filepath_line_1 = f'{DATA_PATH}1_top_10_crimes_per_year.parquet'
    filepath_bar_1 = f'{DATA_PATH}1b_crime_count_total_amount.csv'
    filepath_bar_2 = f'{DATA_PATH}1a_average_crimes_per_hour.parquet'
    
    df_line_1 = load_data(filepath_line_1)
    df_bar_1 = load_data(filepath_bar_1)
    df_bar_2 = load_data(filepath_bar_2)

    # Bar chart 1: Crime types
    st.pyplot(plot_crime_types(df_bar_1))

    st.write("""
    Above we can see all the major categories that are tracked by Chicago Police Department.
    We can clearly see the majority of all crime is concentrated into just a few categories.
    Crimes such as theft currently top over 1.5 million reports or roughly 20.5% of overall reports. Other crimes such as obscenity only account 
    for a very small part counting in at 786 reports, 0.0001%.
    """)

    # Bar chart 2: Crimes by hour
    st.pyplot(plot_crimes_by_hour(df_bar_2))

    st.write("""
    In the graph above we can see the distribution of crime over a 24h period, proving all too well crime never sleeps.
    The distribution of crime throughout the day is to be expected with highs during the day and a steady drop during the evening.

    In the data we can see two spikes at 12:00 and 00:00, from the data it appears to be a software scheduling of some sort,
    or a change of shift. The data clearly shows an abnormal amount of reports specifically at these two times.

    Below you can select and view the top crimes more closely.
    """)

    # Line Graph Multi Select
    crime_types_line = df_line_1['Primary Type'].unique()
    selected_types_line = st.multiselect(
        'Select crime types to display for line graph:', 
        crime_types_line, 
        default=crime_types_line[:3]
    )

    if selected_types_line:
        st.subheader('Crime Trend Analysis')
        st.pyplot(plot_crime_trends(df_line_1, selected_types_line))

    # Line Graph Discuss
    st.subheader('Findings')
    st.write("""
    There are two interesting datapoints that are very visible:

    1. The overall drop in drug related crime in Chicago, this is despite any amount of drugs being considered an offense. On
    further investigation via these articles:

    - [Article One](https://www.chicagoappleseed.org/2022/06/15/dynamics-of-drug-possession-charges-in-illinois/)
    - [Article Two](https://chicago.suntimes.com/2021/11/26/22639255/dead-end-drug-arrests-drugs-possession-chicago)
    - [Article Three](https://chicago.suntimes.com/2022/11/10/23444935/drug-possession-jail-safe-t-act-pretrial-fairness-watchdogs-law-enforcement-cook-county-editorial)
    - [Article Four](https://news.wttw.com/2021/12/07/sun-times-bga-report-reveals-costly-toll-dead-end-drug-arrests)
    """)
    
    st.write("""         
    We can conclude:
             
    1. The majority of all drug arrests are dropped, roughly 86%.
    2. The opioid crisis led to prescription drugs, making it harder for the police to take it away from you.
    3. Marijuana is now legal in Chicago (2022). It is by far the most used drug by the overall population.
    4. Data also suggests that African Americans prefer marijuana over opioids, leading to fewer arrests as it's a lower class drug.

    In short, it's just not worth the effort to pursue misdemeanor offenses in a city where crime is just so high.

    2. Secondly, we can look at the spike in "Motor Vehicle Theft" during and after 2020. The USA saw an increase 
    in car prices as high as 63% over Manufacturer's Suggested Retail Price (MSRP). It's estimated used car prices
    still sit at roughly 32% above the norm. This can be attributed to the decrease in newer cars being produced as shortages 
    in crucial car parts became unavailable. Car manufacturers started producing less-featured cars as a response but were unable to meet demand.
    """)

def plot_covid_timeline(filtered_df):
    """Create line chart showing crime counts during COVID period with annotations"""
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
    filtered_df.set_index('Date', inplace=True)

    lockdown_date = pd.to_datetime('2020-03-31')
    end_lockdown_date = pd.to_datetime('2022-03-31')

    lockdown_count = filtered_df.loc[lockdown_date, 'Count']
    end_lockdown_count = filtered_df.loc[end_lockdown_date, 'Count']

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(filtered_df.index, filtered_df['Count'], marker='o')
    ax.set_title('Number of Reports per Month')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Reports')

    # Lockdown start
    ax.annotate('Lockdown', xy=(lockdown_date, lockdown_count), 
                xytext=(lockdown_date, lockdown_count + 4100),
                arrowprops=dict(arrowstyle='-', linestyle=' ', color='red'), 
                ha='left')
    ax.axvline(x=lockdown_date, color='red', linestyle='--', linewidth=1)

    # Lockdown end
    ax.annotate('Lockdown Ended', xy=(end_lockdown_date, end_lockdown_count), 
                xytext=(end_lockdown_date, end_lockdown_count + 2700),
                arrowprops=dict(arrowstyle='-', linestyle=' ', color='green'), 
                ha='right')
    ax.axvline(x=end_lockdown_date, color='green', linestyle='--', linewidth=1)

    ax.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    
    return fig

def crime_covid():
    st.subheader('Impact of COVID-19 on Crime in Chicago')
    
    filepath_bar_1 = f'{DATA_PATH}3_crime_counts_covid_19.csv'
    filtered_df = load_data(filepath_bar_1)

    st.write("## Number of Reports per Month")
    st.pyplot(plot_covid_timeline(filtered_df))

    st.subheader('Findings Discussion')
    st.write("""
    Overall drop and recovery during and after Covid:
             
        Percentage Change During Lockdown: -39.77%
        Percentage Change After Lockdown: 24.87%
             
    The graph clearly demonstrates that COVID had a massive effect on crime rates in Chicago, dropping to an all-time low.

    In a study published by the College of the Holy Cross by Olivia DiMonte, Advisor: Professor Baumann, on COVID in Chicago and Houston, they were able to
    conclude that for every one case of COVID in Chicago, crime reports fell by 0.25. It should be noted this applies to overall crime;
    however, there were noticeable increases in crimes such as domestic abuse and acts of non-consensual sex.
    """)

def plot_community_crimes(crimes_by_community_area):
    """Create bar chart of crimes by community area"""
    pivot_data_community = crimes_by_community_area.pivot_table(
        index='Community Area', 
        values='Total Crimes', 
        aggfunc='sum'
    )

    fig_community, ax_community = plt.subplots(figsize=(12, 8))
    pivot_data_community.plot(kind='bar', ax=ax_community, color='skyblue')
    ax_community.set_title('Crime Counts by Community Area')
    ax_community.set_ylabel('Total Counts')
    ax_community.set_xlabel('Community Area')
    ax_community.tick_params(axis='x', rotation=90)
    ax_community.grid(True)
    plt.tight_layout()
    
    return fig_community

def community_crime_overview():
    st.subheader('Visual Overview of Crime Distribution')

    st.write("""
    Here we are looking at exploring the overall distribution of crime throughout the city. In the bar graph below, we can see a general distribution across all 76
    communities, with several communities being outliers with abnormally high report rates. Community area 25 soars over all other areas.
    """)
    
    # Add statistics about tourist vs non-tourist areas
    st.warning("""
    **Tourist vs Non-Tourist Areas:**
    
    Our analysis shows a significant disparity in crime rates, with non-tourist areas experiencing 
    248.7% higher crime rates compared to tourist areas. This stark difference highlights the uneven 
    distribution of crime throughout Chicago and the relative safety of areas frequented by visitors.
    """)

    # Load Data
    filepath_crimes_by_community = f'{DATA_PATH}2_crimes_by_community_area.parquet'
    filepath_crimes_by_count_yearly = f'{DATA_PATH}2b_crime_counts_every_year_community.parquet'
    
    crimes_by_year = load_data(filepath_crimes_by_count_yearly)
    crimes_by_community_area = load_data(filepath_crimes_by_community)

    st.subheader('Crime Across City')

    # Bar chart of crimes by community
    st.pyplot(plot_community_crimes(crimes_by_community_area))

    # Map 1: Overall crime by community
    st.title("Chicago Crime Map by Community Area")

    boundary_gdf = load_geojson()
    crimes_by_community_area['Community Area'] = crimes_by_community_area['Community Area'].astype(int)
    boundary_gdf['area_num_1'] = boundary_gdf['area_num_1'].astype(int)
    merged_gdf = boundary_gdf.merge(
        crimes_by_community_area, 
        left_on='area_num_1', 
        right_on='Community Area', 
        how='left'
    )

    map_chicago_1 = create_choropleth_map(
        merged_gdf, 
        'Total Crimes', 
        legend_name='Total Crimes per Community Area'
    )
    folium_static(map_chicago_1)

    st.write('''
    Below you can explore the data year by year. However, it quickly becomes evident that despite the dataset
    spanning over 20+ years, there are several key communities responsible for nearly all crime.
    ''')

    # Map 2: User-selected year
    selected_year = st.selectbox(
        "Select Year", 
        sorted(crimes_by_year.columns[:-1], reverse=True), 
        index=1
    )
    
    selected_year_data = crimes_by_year[['Community Area', selected_year]].copy()
    merged_gdf_year = boundary_gdf.merge(
        selected_year_data, 
        left_on='area_num_1', 
        right_on='Community Area', 
        how='left'
    )
    
    map_chicago_2 = create_choropleth_map(
        merged_gdf_year, 
        selected_year, 
        legend_name=f'Total Crimes per Community Area ({selected_year})'
    )
    folium_static(map_chicago_2)

def create_victim_chart(community_filtered_data, attribute):
    """Create pie chart for victim attributes"""
    if attribute == 'Age':
        fig = px.pie(
            community_filtered_data, 
            names='AGE', 
            values='Count', 
            title='Distribution of Victims by Age'
        )
    elif attribute == 'Sex':
        fig = px.pie(
            community_filtered_data, 
            names='SEX', 
            values='Count', 
            title='Distribution of Victims by Sex'
        )
    elif attribute == 'Race':
        fig = px.pie(
            community_filtered_data, 
            names='RACE', 
            values='Count', 
            title='Distribution of Victims by Race'
        )
    else:
        return None
        
    return fig

def shootings_fatalities():
    st.subheader('Shootings across Chicago')
    
    # Add homicide statistics
    st.error("""
    **Homicide Statistics:**
    - Average annual homicides: 534.0
    - Per 100,000 population: 19.8 (population: 2,700,000)
    - This rate is significantly higher than the [national average](https://www.cdc.gov/nchs/fastats/homicide.htm?utm_source=chatgpt.com)
    """)
    
    boundary_gdf = load_geojson()
    community_df = load_parquet(f'{DATA_PATH}4a_shootings_and_deaths.parquet')

    merged_gdf = boundary_gdf.merge(
        community_df, 
        left_on='community', 
        right_on='COMMUNITY_AREA', 
        how='left'
    )

    # Map
    map_community = create_choropleth_map(
        merged_gdf, 
        'Homicides', 
        legend_name='Homicides per Community Area'
    )
    folium_static(map_community)

    st.write('''
    In the map above, you can clearly see that the same areas tend to be highlighted regardless of the 
    data being visualized. The map shows all homicides - shootings leading to death since 1991. However, it should be
    noted that non-fatal shootings were not recorded until 2010. 

    Below you can dive deeper into the data, looking at Age, Sex, and Race of all victims - fatal and non-fatal -
    for each community area.
    ''')

    st.subheader('Explore Community Victim Details')

    csv_data = load_csv(f'{DATA_PATH}4_alt_victim_counts_with_overview.csv')

    # User Select
    community_areas = sorted(csv_data['COMMUNITY_AREA'].unique())
    selected_area = st.selectbox('Select a Community Area:', community_areas)

    community_filtered_data = csv_data[csv_data['COMMUNITY_AREA'] == selected_area]

    # Community victim data analysis
    if not community_filtered_data.empty:
        # Allow the user to select the attribute for further analysis
        selected_attribute = st.selectbox(
            'Select Attribute for Analysis:', 
            ['Age', 'Sex', 'Race']
        )

        chart = create_victim_chart(community_filtered_data, selected_attribute)
        if chart:
            st.plotly_chart(chart)
        else:
            st.write('Invalid attribute selected.')
    else:
        st.write('No victim data available for the selected community area.')

def conclusion():
    st.title("Conclusion")

    # Key statistics callout
    st.info("""
    **Key Statistics:**
    - Average homicides per year: 534.0
    - Homicide rate: 19.8 per 100,000 inhabitants (population of 2,700,000)
    - This rate is significantly higher than the [national average](https://www.cdc.gov/nchs/fastats/homicide.htm?utm_source=chatgpt.com)
    - Crime rate difference: 248.7% higher in non-tourist areas compared to tourist areas
    """)

    st.write('''
    In conclusion to the findings of the data exploration, we have confidently been able to answer the questions
    we sought to answer. Although the crime rate is overwhelmingly high in Chicago, it is still safer in the more tourist-related areas,
    with a striking 248.7% difference in crime rates between tourist and non-tourist areas.
    
    Chicago's average of 534 homicides per year translates to approximately 19.8 homicides per 100,000 inhabitants, 
    significantly higher than the national average.
    
    Unfortunately, due to the dataset, we are unable to see the surrounding areas to the high-crime communities. This would allow 
    us to more concretely see if crime extends outwards to the city, especially in high African American communities.

    Key findings from our analysis:
    
    1. Crime has shifted in types over the past two decades, with significant decreases in drug-related offenses
    2. COVID-19 had a dramatic impact on overall crime rates, with specific types of crimes showing different patterns
    3. Crime is heavily concentrated in specific community areas of Chicago
    4. Gun violence follows similar geographical patterns to overall crime rates
    5. Demographics of shooting victims show clear patterns across different communities
    ''')

def main():
    # Page navigation
    page_options = {
        "Welcome": welcome,
        "Crime Analysis": crime_analysis, 
        "Crime During Covid": crime_covid,
        "Visual Overview of Crime": community_crime_overview,
        "Victims of Shootings": shootings_fatalities,
        "Conclusion": conclusion
    }
    
    page_selection = st.sidebar.radio(
        "Navigate to Different Pages:", 
        list(page_options.keys())
    )
    
    # Call the selected page function
    page_options[page_selection]()

if __name__ == '__main__':
    main()