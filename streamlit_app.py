import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be: ", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to Pandas for easier manipulation
pd_df = my_dataframe.to_pandas()

# Let user select ingredients
ingredients_lists = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Display nutrition info and submit order
if ingredients_lists:
    ingredients_string = ''

    for fruit_chosen in ingredients_lists:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write(f'The search value for {fruit_chosen} is {search_on}.')

        st.header(f"{fruit_chosen} Nutrition Information")

        # Fetch nutrition data
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        fv_df = st.dataframe(data=response.json(),use _container_width = True)

    # Submit to Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!')
