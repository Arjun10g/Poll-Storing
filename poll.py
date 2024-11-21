import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.markdown(
    """
    <style>
    /* Main page styling */
    .main {
        background-color: #f9f9f9;
        font-family: Arial, sans-serif;
    }
    
    /* Title and headers */
    h1 {
        color: black;
        font-weight: bold;
        letter-spacing:3px;
        text-shadow: 2px 1px 2px white;
        font-size: 2.5rem;
    }
    h2, h3, h4 {
        color: white;
        letter-spacing:2px;
        text-decoration:underline;
        text-underline-offset: 6px;
        font-size:1.45rem;
    }

    /* Custom text area styling */
    textarea {
        border: 2px solid #004085;
        border-radius: 5px;
        padding: 10px;
        font-size: 1.1rem;
    }

    /* Button styling */
    button {
        background-color: #004085;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 1rem;
        cursor: pointer;
    }
    button:hover {
        background-color: white;
        color:black;
    }

    /* Sidebar styling */
    .st-sidebar {
        background-color: #f1f4f9;
    }

    /* Word Cloud styling */
    .wordcloud-container {
        text-align: center;
        margin: 20px 0;
    }

    /* Adjust chart size */
    .stPlotlyChart, .stPyplot {
        max-width: 90%;
        margin: auto;
    }

    /* Admin section styling */
    .admin-section {
        padding: 20px;
        background-color: #e9ecef;
        border: 1px solid #004085;
        border-radius: 5px;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

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
def save_response(opinion, ai_scale, main_reason, ai_adoption):
    conn = create_connection()
    cursor = conn.cursor()
    
    transcription = ai_adoption["Transcription"]
    initial_coding = ai_adoption["Initial Coding"]
    all_coding = ai_adoption["All Coding"]
    interpretation = ai_adoption["Interpretation"]
    writing = ai_adoption["Writing"]

    cursor.execute("""
        INSERT INTO poll_responses (opinion, ai_scale, main_reason, transcription, initial_coding, all_coding, interpretation, writing)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (opinion, ai_scale, main_reason, transcription, initial_coding, all_coding, interpretation, writing))
    
    conn.commit()
    cursor.close()
    conn.close()

# Function to load data from the database
def load_data():
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM poll_responses", conn)
    conn.close()
    return df

# Function to display Likert-style responses as numeric summaries
def display_likert_summary(df, columns):
    st.subheader("Likert Scale Responses Summary")
    for column in columns:
        st.write(f"**{column}**")
        
        # Convert column to numeric, forcing errors to NaN
        df[column] = pd.to_numeric(df[column], errors='coerce')
        
        counts = df[column].value_counts().sort_index()
        st.bar_chart(counts, use_container_width=True)
        
        # Display summary statistics
        mean = df[column].mean()
        median = df[column].median()
        std_dev = df[column].std()
        st.write(f"Mean: {mean:.2f}, Median: {median}, Std Dev: {std_dev:.2f}")

# Function to display a word cloud, even for empty data
def display_wordcloud(data, column):
    if data[column].dropna().empty:
        st.write(f"No data available for {column}.")
    else:
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
main_reason = st.text_area("What is the main reason you are not currently using AI-based tools?")

# Dynamic Likert-scale items with numeric values
st.subheader("How likely are you to adopt AI for each step of qualitative research?")
likert_mapping = {
    "Very unlikely": 1,
    "Unlikely": 2,
    "Neutral": 3,
    "Likely": 4,
    "Very likely": 5
}
ai_adoption = {}
for step in ["Transcription", "Initial Coding", "All Coding", "Interpretation", "Writing"]:
    response = st.radio(f"Adoption for {step}:", list(likert_mapping.keys()), key=f"adoption_{step}")
    ai_adoption[step] = likert_mapping[response]  # Save as numeric value

if st.button("Submit"):
    save_response(opinion, ai_scale, main_reason, ai_adoption)
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

            # Display word cloud for main reasons not using AI
            st.subheader("Word Cloud of Reasons for Not Using AI")
            display_wordcloud(df, "main_reason")
            
            # Display Likert-scale items as bar charts
            st.subheader("Summary of Likert-Scale AI Adoption Choices")
            display_likert_summary(df, ["transcription", "initial_coding", "all_coding", "interpretation", "writing"])
        else:
            st.write("No responses yet.")
    else:
        st.error("Incorrect password. Access denied.")

# cd "/Users/arjunghumman/Downloads/VS Code Stuff/Python/Poll Storing"
# streamlit run poll.py
    