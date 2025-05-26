## Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)


name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be: ", name_on_order)

cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options"). select (col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert the Snowpark Dataframe to a Panda Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

ingredients_lists = st.multiselect(
    'Choose upto 5 ingredients: '
    , my_dataframe
    , max_selections=5
) 


if ingredients_lists:
    ingredients_string = ''

    for fruit_chosen in ingredients_lists:
        ingredients_string += fruit_chosen + ' ' 
      
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.header(fruit_chosen + 'Nutrition Information')
        fruityvice_response = requests.get("https://my.fruityvice.com/api/fruit/" + fruit_chosen)
        sf_df = st.dataframe(data=fruityvice_response.json(), use_container_width = True)

   #st.write (ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""


  #st.write(my_insert_stmt)
    time_to_insert = st.button('SubmitOrder')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()   
        st.success(f'Your Smoothie is ordered, {name_on_order}!')


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

# Connect to Snowflake
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Fetch fruit options
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(
        col('FRUIT_NAME'), col('SEARCH_ON')
    )
    pd_df = my_dataframe.to_pandas()

    # Get list of fruit names for the dropdown (but do not display the table)
    fruit_options = pd_df['FRUIT_NAME'].dropna().tolist()

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

            # Fetch nutrition info
            response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen.lower())
            if response.status_code == 200:
                st.header(f"{fruit_chosen} Nutrition Information")
                st.json(response.json())
            else:
                st.warning(f"No nutrition info found for {fruit_chosen}.")

        # Insert SQL
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """

        if st.button('Submit Order'):
            session.sql(insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!")

except Exception as e:
    st.error(f"An error occurred: {e}")
