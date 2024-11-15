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
def save_response(opinion, ai_scale, challenges, ai_adoption, reason_not_using_ai):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Extract individual responses from ai_adoption
    transcription = ai_adoption["Transcription"]
    initial_coding = ai_adoption["Initial Coding"]
    all_coding = ai_adoption["All Coding"]
    interpretation = ai_adoption["Interpretation"]
    writing = ai_adoption["Writing"]
    
    cursor.execute("""
        INSERT INTO poll_responses (opinion, ai_scale, challenges, transcription, initial_coding, all_coding, interpretation, writing, reason_for_not_using_ai)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (opinion, ai_scale, challenges, transcription, initial_coding, all_coding, interpretation, writing, reason_not_using_ai))
    
    conn.commit()
    cursor.close()
    conn.close()

# Function to load data from the database
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

# Function to display horizontal bar charts
def display_horizontal_bar(df, column, title):
    response_counts = df[column].value_counts()
    
    plt.figure(figsize=(10, 6))
    plt.barh(response_counts.index, response_counts.values, color='skyblue')
    plt.xlabel("Number of Responses")
    plt.ylabel("Options")
    plt.title(title)
    st.pyplot(plt)

# Streamlit app layout
st.title("AI in Research Poll")

# Collect responses
st.header("Your Opinion Matters!")
opinion = st.text_area("What are your initial opinions towards AI in research?")
ai_scale = st.slider("How do you feel about the use of AI on a scale of 1-10?", 1, 10, 5)
challenges = st.text_area("What are the difficulties or challenges of qualitative research?")

# Dynamic MCQ for AI adoption
st.subheader("How likely are you to adopt AI for each step of qualitative research?")
ai_adoption_choices = {
    "Transcription": [
        "Use real-time transcription using AI tools",
        "Use automated transcription with manual review",
        "I would, but only if Victoria/Arjun walk me through it",
        "Fully manual transcription"
    ],
    "Initial Coding": [
        "Use AI topic modeling tools that categorize sentences for me, and name them",
        "Manual coding with AI suggesting themes",
        "I would, but only if Victoria/Arjun walk me through it",
        "Fully manual theme identification"
    ],
    "All Coding": [
        "Use AI-assisted coding for everything",
        "Use supervised learning to automate coding",
        "AI for initial coding, then manual refinement",
        "I would, but only if Victoria/Arjun walk me through it",
        "Fully manual coding"
    ],
    "Interpretation": [
        "AI-powered summarization and interpretation",
        "Manual interpretation supported by AI visualizations",
        "I would, but only if Victoria/Arjun walk me through it",
        "Fully manual interpretation"
    ],
    "Writing": [
        "Use AI for report drafting (e.g., ChatGPT)",
        "Grammarly for grammar and style checks only",
        "AI-assisted data visualization and summaries",
        "I would, but only if Victoria/Arjun walk me through it",
        "Fully manual report writing"
    ]
}

ai_adoption = {}
for step, options in ai_adoption_choices.items():
    ai_adoption[step] = st.radio(f"Adoption for {step}:", options, key=f"adoption_{step}")

# New question: Reasons for not implementing AI
st.subheader("What is the main reason you are not currently using AI-based tools?")
reason_not_using_ai = st.radio(
    "Select the main reason:",
    [
        "Ethical concerns about AI",
        "Lack of knowledge on how to implement AI",
        "Lack of trust in the accuracy of AI tools",
        "Cost or resource constraints",
        "Belief that manual methods are more reliable"
    ],
    key="reason_not_using_ai"
)

if st.button("Submit"):
    save_response(opinion, ai_scale, challenges, ai_adoption, reason_not_using_ai)
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
            
            # Display horizontal bar charts for each AI adoption step
            st.subheader("Horizontal Bar Charts for AI Adoption Choices")
            for step in ai_adoption_choices.keys():
                display_horizontal_bar(df, step.lower().replace(' ', '_'), f"Responses for {step}")
            
            # Display reasons for not using AI as a bar chart
            st.subheader("Reasons for Not Using AI")
            display_horizontal_bar(df, "reason_for_not_using_ai", "Main Reasons for Not Using AI-Based Tools")
        else:
            st.write("No responses yet.")
    else:
        st.error("Incorrect password. Access denied.")

# cd "/Users/arjunghumman/Downloads/VS Code Stuff/Python/Poll Storing"
# streamlit run poll.py
    