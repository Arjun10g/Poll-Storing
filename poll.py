import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Database connection setup
def create_connection():
    conn = psycopg2.connect(
        host="pollmaster.postgres.database.azure.com",  # Your Azure PostgreSQL server
        database="postgres",  # Name of your database
        user="pollmaster",  # Your Azure PostgreSQL username
        password="Rocky_1995",  # Your Azure PostgreSQL password
        sslmode="require"  # Ensures secure connection
    )
    return conn

# Insert data into the database
def save_response(opinion, ai_scale, challenges):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO poll_responses (opinion, ai_scale, challenges)
        VALUES (%s, %s, %s)
    """, (opinion, ai_scale, challenges))
    conn.commit()
    cursor.close()
    conn.close()

# Load data for visualization
def load_data():
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM poll_responses", conn)
    conn.close()
    return df

# Function to display a word cloud
def display_wordcloud(data, column):
    text = " ".join(data[column].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

# Streamlit app layout
st.title("AI in Research Poll")

# Collect responses
st.header("Your Opinion Matters!")
opinion = st.text_area("What are your initial opinions towards AI in research?")
ai_scale = st.slider("How do you feel about the use of AI on a scale of 1-10?", 1, 10, 5)
challenges = st.text_area("What are the difficulties or challenges of qualitative research?")

if st.button("Submit"):
    save_response(opinion, ai_scale, challenges)
    st.success("Thank you for your response!")

# Password-protected section
st.header("Admin Access: Poll Results")
admin_password = st.text_input("Enter Admin Password:", type="password")

if st.button("Access Results"):
    if admin_password == "qualitative":  # Replace with your actual password
        st.success("Access granted!")
        
        df = load_data()

        if not df.empty:
            # Add unique IDs for each response
            df['response_id'] = range(1, len(df) + 1)

            # Display the scale responses as a bar chart
            st.subheader("Scale Responses (1-10)")
            st.bar_chart(df.set_index('response_id')['ai_scale'])

            # Display word cloud for opinions
            st.subheader("Word Cloud of Open-Ended Opinions")
            display_wordcloud(df, "opinion")

            # Display word cloud for challenges
            st.subheader("Word Cloud of Challenges")
            display_wordcloud(df, "challenges")
        else:
            st.write("No responses yet.")
    else:
        st.error("Incorrect password. Access denied.")




# cd "/Users/arjunghumman/Downloads/VS Code Stuff/Python/Poll Storing"
# streamlit run poll.py
    