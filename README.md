# Chicago Crime Dashboard

## Project Overview
This Streamlit-based dashboard visualizes and analyzes crime data in Chicago from 2001 to the present day. Using data from the [Chicago Data Portal](https://data.cityofchicago.org), this application provides interactive visualizations and insights into crime patterns across Chicago's communities, with a particular focus on:

1. How crime has changed over the last 20 years
2. Why narcotic crimes have decreased over time despite high drug use
3. How crime is distributed geographically across the city
4. How COVID-19 affected crime rates
5. The distribution of shootings and homicides

## Data Sources
- **Main Crime Dataset**: [Chicago Crime Data (2001-Present)](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2/data) - Contains over 8 million recorded crimes
- **Shooting Data**: A separate comprehensive dataset on shootings across Chicago
- **Geographical Data**: Chicago community area boundaries in GeoJSON format

## Features

### Pages
The dashboard consists of the following pages:
1. **Welcome**: Introduction to the project and main research questions
2. **Crime Analysis**: Overview of crime types and temporal distribution
3. **Crime During COVID**: Analysis of how the pandemic affected crime rates
4. **Visual Overview of Crime**: Geographic distribution of crime across communities
5. **Victims of Shootings**: Analysis of shooting patterns and demographics
6. **Conclusion**: Summary of key findings

### Key Visualizations
- Bar charts showing crime types and distributions
- Time series analysis of crime patterns
- Interactive maps using Folium for geographic crime distribution
- Choropleth maps highlighting high-crime areas
- Demographic breakdowns of shooting victims by age, race, and gender

### Key Findings
- Average of 534 homicides per year (19.8 per 100,000 inhabitants)
- 248.7% higher crime rates in non-tourist areas compared to tourist areas
- Significant drop in narcotic crimes over time (despite high drug use)
- Dramatic impact of COVID-19 on crime patterns
- Concentrated crime distribution in specific community areas

## Technical Implementation

### Core Components
- `chicago_crime.py`: Main Streamlit application file
- Notebooks: Data preparation and exploratory analysis
- Data caching system for improved performance

### Key Libraries
- Streamlit: For the interactive web interface
- Pandas/Geopandas: For data manipulation and analysis
- Matplotlib/Plotly: For data visualization
- Folium: For interactive maps

### Data Preparation
The project uses a data caching system to enhance performance:
- Large CSV datasets are converted to Parquet format for faster loading
- Pre-processed datasets are stored in the `data/data_cache/` directory
- All visualizations leverage cached data for improved responsiveness

## Getting Started

### Prerequisites
- Python 3.9+
- Required libraries listed in requirements.txt

### Installation
1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Download the necessary datasets:
   - The main Chicago crime dataset
   - Chicago community area boundaries GeoJSON
   - Shooting victims dataset (if analyzing this separately)

4. Place the datasets in the `data/` directory
5. Run the preprocessing notebook(s) to generate the cached data files
6. Run the Streamlit application:
   ```
   streamlit run chicago_crime.py
   ```

## Project Structure
```
/
├── chicago_crime.py          # Main Streamlit application
├── chicago_crime_analysis.ipynb  # Exploratory data analysis notebook
├── compressor.ipynb          # Data caching and preparation notebook
├── data/
│   ├── chicago_boundaries.geojson  # Community area boundaries
│   ├── crime_data.parquet    # Main crime dataset (converted)
│   ├── gun_crime_chicago.csv # Shooting data
│   └── data_cache/           # Preprocessed data for visualizations
│       ├── 1_top_10_crimes_per_year.parquet
│       ├── 1a_average_crimes_per_hour.parquet
│       ├── 1b_crime_count_total_amount.csv
│       ├── 2_crimes_by_community_area.parquet
│       ├── 2b_crime_counts_every_year_community.parquet
│       ├── 3_crime_counts_covid_19.csv
│       ├── 4_alt_victim_counts_with_overview.csv
│       └── 4a_shootings_and_deaths.parquet
└── requirements.txt          # Required Python packages
```

## Notebook Information

### chicago_crime_analysis.ipynb
This notebook contains the exploratory data analysis (EDA) for the project. Key features:
- Data cleaning and preprocessing
- Initial visualizations and pattern detection
- Crime trend analysis over time
- COVID-19 impact analysis
- Community area analysis and mapping
- Crime distribution across different demographics

### compressor.ipynb
This notebook focuses on data preparation and caching:
- Converts large CSV files to Parquet format for better performance
- Creates aggregated datasets for various visualizations
- Generates the necessary cached files for the Streamlit dashboard
- Handles geocoding and spatial data preparation

## Acknowledgments
- City of Chicago for providing the open crime data
- The Chicago Sun Times and other sources for contextual information on crime trendsFiller
