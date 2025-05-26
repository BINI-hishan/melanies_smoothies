# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Create Snowflake connection
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Get name input
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be:", name_on_order)

# Get fruit options from the Snowflake table
try:
    fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
    fruit_list = fruit_df["FRUIT_NAME"].tolist()
except Exception as e:
    st.error(f"Error loading fruit options: {e}")
    fruit_list = []

# Multiselect for fruit ingredients
ingredients_lists = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Submit order
if ingredients_lists:
    ingredients_string = ', '.join(ingredients_lists)  # Join nicely with commas
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!")
        except Exception as e:
            st.error(f"Failed to insert order: {e}")
