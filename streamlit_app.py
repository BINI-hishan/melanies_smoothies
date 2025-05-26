# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title
st.title("🥤 Customize Your Smoothie 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Fetch fruit options
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(
        col('FRUIT_NAME'), col('SEARCH_ON')
    )
    pd_df = my_dataframe.to_pandas()

    if pd_df.empty:
        st.warning("No fruit options found in database.")
    else:
        # Display fruit options
        st.subheader("Available Fruit Options:")
        st.dataframe(pd_df)

        # Extract fruit names for multiselect
        fruit_options = pd_df['FRUIT_NAME'].dropna().tolist()

        # DEBUG print
        st.write("Fruit options loaded:", fruit_options)

        # Multiselect for ingredients
        ingredients_lists = st.multiselect(
            'Choose up to 5 ingredients:',
            fruit_options,
            max_selections=5
        )

        if ingredients_lists:
            ingredients_string = ' '.join(ingredients_lists)

            for fruit_chosen in ingredients_lists:
                search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
                st.write(f"The search value for {fruit_chosen} is {search_on}.")

                # API request
                response = requests.get("https://my.fruityvice.com/api/fruit/" + fruit_chosen.lower())
                if response.status_code == 200:
                    st.header(f"{fruit_chosen} Nutrition Information")
                    st.json(response.json())
                else:
                    st.warning(f"No nutrition info found for {fruit_chosen}.")

            # Insert SQL statement
            insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """

            # Submit button
            if st.button('Submit Order'):
                session.sql(insert_stmt).collect()
                st.success(f"Your Smoothie is ordered, {name_on_order}!")

except Exception as e:
    st.error(f"An error occurred: {e}")
