# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title and instructions
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Get Snowflake connection and session
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Input for smoothie order name
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be: ", name_on_order)

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark DataFrame to pandas
pd_df = my_dataframe.to_pandas()

# Display available fruit options
fruit_list = pd_df['FRUIT_NAME'].tolist()
ingredients_lists = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# If ingredients selected, display nutrition and insert option
if ingredients_lists:
    ingredients_string = ''

    for fruit_chosen in ingredients_lists:
        ingredients_string += fruit_chosen + ' '

        search_row = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']

        if not search_row.empty:
            search_on = search_row.iloc[0].strip()

            st.subheader(fruit_chosen + ' Nutrition Information')
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)

            if fruityvice_response.status_code == 200:
                fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
            else:
                st.error(f"API error for {fruit_chosen}: {fruityvice_response.status_code}")
        else:
            st.warning(f"No 'SEARCH_ON' value found for {fruit_chosen}")

    # Submit order button
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!')
