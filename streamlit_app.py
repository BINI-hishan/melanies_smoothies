import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for smoothie name
name_on_order = st.text_input('Name on Smoothie:')
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Get fruit options from Snowflake
fruit_df = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
).to_pandas()

# Let user select ingredients
ingredients_selected = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Display nutrition info and submit order
if ingredients_selected:
    st.subheader("Nutrition Information")
    ingredients_string = ", ".join(ingredients_selected)

    for fruit in ingredients_selected:
        search_on = fruit_df.loc[fruit_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        response = requests.get(f"https://my.fruityvice.com/api/fruit/{search_on}")
        
        if response.status_code == 200:
            fruit_data = pd.json_normalize(response.json())
            st.write(f"**{fruit}**")
            st.dataframe(fruit_data, use_container_width=True)
        else:
            st.warning(f"Could not retrieve data for {fruit}.")

    # Submit to Snowflake
    if st.button('Su
