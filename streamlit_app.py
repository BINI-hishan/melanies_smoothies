## Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Set up the app
st.title("🥤 Customize Your Smoothie 🥤")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Get the user's name
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Query the available fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)

# Convert to pandas for display and filtering
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

# Convert fruit names to list for multiselect
fruit_options = pd_df['FRUIT_NAME'].tolist()

# Let the user choose ingredients
ingredients_lists = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

# If the user selected fruits, process the order
if ingredients_lists:
    ingredients_string = ' '.join(ingredients_lists)

    for fruit_chosen in ingredients_lists:
        # Get the search value for the fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        # Get nutrition information from Fruityvice API
        fruityvice_response = requests.get("https://my.fruityvice.com/api/fruit/" + fruit_chosen.lower())
        if fruityvice_response.status_code == 200:
            st.header(f"{fruit_chosen} Nutrition Information")
            st.json(fruityvice_response.json())
        else:
            st.error(f"Could not get nutrition info for {fruit_chosen}")

    # SQL Insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!')
