import pysqlite3 as sqlite3  # Use pysqlite3 instead of sqlite3 for compatibility with ChromaDB
import streamlit as st
import requests
import fitz  # PyMuPDF for PDF scraping
from crewai import Agent, AgentManager

# Show title and description
st.title("🏫 Angel and Devil School Finder Chatbot")
st.write(
    "Welcome to the Angel and Devil School Finder Chatbot! 🎒\n\n"
    "This chatbot helps you find the right secondary school by giving you two perspectives:\n\n"
    "- **Angel**: Advocates for schools that align with your passions, strengths, and preferences.\n"
    "- **Devil**: Points out practical considerations, such as proximity to home, academic fit, and logistical concerns.\n"
    "- **Student Councillor**: Provides neutral, factual information on school programmes, CCAs, and more.\n\n"
    "You can ask specific questions like \"ask Student Councillor\" for school details or request \"I need the Angel and Devil to weigh in\" to hear both perspectives.\n"
    "If you’re unsure, I’ll default to the Student Councillor for general school information.\n\n"
    "**How to Use This Chatbot**:\n"
    "1. **Ask questions** about school details or for opinions on school choices.\n"
    "2. **Specify if you want Angel and Devil to weigh in** by including \"I need the Angel and Devil to weigh in\" in your question.\n"
    "3. **Receive a personalised list of recommended schools** based on your preferences.\n\n"
    "Let’s get started on finding your ideal school!"
)

# Password protection setup
password_input = st.text_input("Enter Password:", type="password")
if password_input != st.secrets["password"]:
    st.error("Incorrect password. Please try again.")
    st.stop()  # Stop further execution if the password is incorrect

# Retrieve the OpenAI API key from secrets
openai_api_key = st.secrets["openai_api_key"]
if not openai_api_key:
    st.error("OpenAI API key is missing in secrets.toml.")
    st.stop()  # Stop if no API key is provided

# Define Angel, Devil, and Student Councillor agents with updated personalities and example dialogues
angel_agent = Agent(
    name="Angel",
    description="A positive and encouraging guide for students choosing secondary schools.",
    personality="optimistic, supportive, solution-oriented, personalised",
    role="Highlights potential benefits and aligns school options with the student's goals and aspirations.",
    tone="Sympathetic, friendly, and encouraging, using UK spelling",
    dialogue_style="Conversational English with UK spelling, balanced with Devil Bot for constructive debate",
    additional_traits="Acknowledges anxieties, provides constructive solutions, and highlights personalised benefits of each option"
)

devil_agent = Agent(
    name="Devil",
    description="A realistic and pragmatic advisor who emphasises logistical concerns and challenges.",
    personality="realistic, thought-provoking, cautious, individualised",
    role="Raises important questions, prompts critical thinking, and points out potential challenges in each school option",
    tone="Direct, slightly mischievous, uses Singlish with UK spelling",
    dialogue_style="Playful banter and tag-teaming with Angel Bot, Singlish to make conversations relatable",
    additional_traits="Highlights potential challenges and thought-provoking questions to help users consider practical limitations"
)

student_councillor_agent = Agent(
    name="Student Councillor",
    description="A friendly and knowledgeable guide who provides factual information about school programs, CCAs, and other school-related details.",
    personality="welcoming, friendly, knowledgeable, organised, impartial",
    role="Provides neutral, detailed, and accurate information about the school system, specific schools, programs, and CCAs.",
    tone="Friendly and approachable, with standard UK English.",
    dialogue_style="Neutral, helpful, and clear"
)

# Initialize the AgentManager with all three agents
agent_manager = AgentManager(agents=[angel_agent, devil_agent, student_councillor_agent])

# Function to download and parse the PSLE info sheet PDF content
def get_psle_info():
    url = "https://www.moe.gov.sg/microsites/psle-fsbb/assets/infographics/new-psle-scoring-system/psle-infosheet-english.pdf"
    response = requests.get(url)

    with open("psle_infosheet.pdf", "wb") as file:
        file.write(response.content)
    
    # Parse the PDF content
    psle_content = ""
    with fitz.open("psle_infosheet.pdf") as pdf:
        for page in pdf:
            psle_content += page.get_text()
    
    return psle_content

# Retrieve and store the PSLE info content in memory
psle_info_content = get_psle_info()

# Function to search the PSLE info content for relevant data
def search_psle_info(query):
    lines = psle_info_content.split("\n")
    relevant_lines = [line for line in lines if query.lower() in line.lower()]
    return "\n".join(relevant_lines) if relevant_lines else "Information on this topic is not available in the PSLE info sheet."

# Function to query the Singapore OpenAPI for school collection data
def get_school_collection_data():
    collectionId = 457          
    url = f"https://api-production.data.gov.sg/v2/public/api/collections/{collectionId}/metadata"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch data from OpenAPI."}

# Student Councillor's response logic with PDF and API integration
def get_student_councillor_response(prompt):
    if "school data" in prompt.lower():
        school_data = get_school_collection_data()
        return school_data
    elif "psle" in prompt.lower() or "scoring" in prompt.lower():
        return search_psle_info(prompt)
    return "I'm here to help with questions about school programs, CCAs, and more. Feel free to ask!"

# Define function to determine response type based on prompt
def get_response_type(prompt):
    if "i need the angel and devil to weigh in" in prompt.lower():
        return "angel_and_devil"
    elif "ask student councillor" in prompt.lower() or is_informational_query(prompt):
        return "student_councillor"
    else:
        return "student_councillor"  # Default to Student Councillor for non-specific queries

# Check if prompt is an informational query
def is_informational_query(prompt):
    informational_keywords = ["program", "CCA", "school info", "subject", "facility", "details"]
    return any(keyword in prompt.lower() for keyword in informational_keywords)

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Text input for the user's message
if prompt := st.chat_input("How can I help you with your school search?"):

    # Store and display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Determine the response type based on trigger phrases
    response_type = get_response_type(prompt)

    # Fetch response based on type
    try:
        if response_type == "student_councillor":
            # Get response from Student Councillor with PSLE info and API data
            response_text = get_student_councillor_response(prompt)
            agent_name = "Student Councillor Bot"
            with st.chat_message(agent_name):
                st.markdown(response_text)
            st.session_state.messages.append({"role": agent_name, "content": response_text})

        elif response_type == "angel_and_devil":
            # Get responses from both Angel and Devil
            responses = agent_manager.get_responses(prompt)
            for response in responses:
                agent_name = "Angel Bot" if response["agent"] == "Angel" else "Devil Bot"
                agent_message = response["message"]
                with st.chat_message(agent_name):
                    st.markdown(agent_message)
                st.session_state.messages.append({"role": agent_name, "content": agent_message})

    except Exception as e:
        st.error(f"An error occurred while fetching responses: {e}")
