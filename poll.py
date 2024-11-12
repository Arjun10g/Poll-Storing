import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Database setup
DB_HOST = "pollresponseserver.postgres.database.azure.com"
DB_NAME = "postgres"
DB_USER = "pollmaster@pollresponseserver"
DB_PASSWORD = "Rocky_1995"

# Connect to PostgreSQL
def init_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

conn = init_connection()
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS poll_responses (
    id SERIAL PRIMARY KEY,
    opinion TEXT,
    ai_scale INTEGER,
    challenges TEXT
)
''')
conn.commit()

# Insert data into the database
def save_response(opinion, ai_scale, challenges):
    c.execute(
        sql.SQL("INSERT INTO poll_responses (opinion, ai_scale, challenges) VALUES (%s, %s, %s)"),
        (opinion, ai_scale, challenges)
    )
    conn.commit()

# Load data for visualization
def load_data():
    df = pd.read_sql_query("SELECT * FROM poll_responses", conn)
    return df

# App layout
st.title("AI in Research Poll")

# Collect responses
st.header("Your Opinion Matters!")
opinion = st.text_area("What are your initial opinions towards AI in research?")
ai_scale = st.slider("How do you feel about the use of AI on a scale of 1-10?", 1, 10, 5)
challenges = st.text_area("What are the difficulties or challenges of qualitative research?")

if st.button("Submit"):
    save_response(opinion, ai_scale, challenges)
    st.success("Thank you for your response!")

# Data visualization
st.header("Poll Results")

df = load_data()

if not df.empty:
    st.subheader("Scale Responses (1-10)")
    st.bar_chart(df['ai_scale'].value_counts().sort_index())

    st.subheader("Word Cloud of Open-Ended Opinions")
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(df['opinion'].dropna()))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

    st.subheader("Word Cloud of Challenges")
    challenges_cloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(df['challenges'].dropna()))
    plt.figure(figsize=(10, 5))
    plt.imshow(challenges_cloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)
else:
    st.write("No responses yet.")

# Close the connection when done
conn.close()

