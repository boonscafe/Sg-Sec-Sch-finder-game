import sys
import json
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

# Import necessary libraries
import chromadb
import streamlit as st
import requests
import fitz  # PyMuPDF for PDF scraping
from crewai import Agent  # Only import Agent, omitting AgentManager
import openai  # Import OpenAI for smart replies

# Initialize session state for chat messages if it doesn't already exist
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets.get("openai_api_key")
# Check to ensure the API key is available
if openai.api_key is None:
    st.error("OpenAI API key is missing. Please configure it in Streamlit secrets.")

# Initialize ChromaDB client
chroma_client = chromadb.Client()  # No need for Config class here

# Set up sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "About Us", "Methodology"])

# Display the selected page
if page == "Home":
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

elif page == "About Us":
    import About_Us

elif page == "Methodology":
    import Methodology

# Define Agent instances with necessary attributes
angel_agent = Agent(
    name="Angel",
    description="A positive and encouraging guide for students choosing secondary schools.",
    personality="optimistic, supportive, solution-oriented, personalised",
    role="Highlights potential benefits and aligns school options with the student's goals and aspirations.",
    tone="Sympathetic, friendly, and encouraging, using UK spelling",
    dialogue_style="Conversational English with UK spelling, balanced with Devil Bot for constructive debate",
    additional_traits="Acknowledges anxieties, provides constructive solutions, and highlights personalised benefits of each option",
    goal="To help students find schools that align with their strengths and interests",
    backstory="An experienced educational advisor with a passion for helping students succeed in the right environment."
)

devil_agent = Agent(
    name="Devil",
    description="A realistic and pragmatic advisor who emphasises logistical concerns and challenges.",
    personality="realistic, thought-provoking, cautious, individualised",
    role="Raises important questions, prompts critical thinking, and points out potential challenges in each school option",
    tone="Direct, slightly mischievous, uses Singlish with UK spelling",
    dialogue_style="Playful banter and tag-teaming with Angel Bot, Singlish to make conversations relatable",
    additional_traits="Highlights potential challenges and thought-provoking questions to help users consider practical limitations, like distance, friends",
    goal="To ensure students make well-considered, practical school choices",
    backstory="A practical advisor who values logical decision-making and enjoys challenging students to think realistically."
)

student_councillor_agent = Agent(
    name="Student Councillor",
    description="A friendly and knowledgeable guide who provides factual information about school programs, CCAs, and other school-related details.",
    personality="welcoming, friendly, knowledgeable, organised, impartial",
    role="Provides neutral, detailed, and accurate information about the school system, specific schools, programs, and CCAs.",
    tone="Friendly and approachable, with standard UK English.",
    dialogue_style="Neutral, helpful, and clear",
    goal="To inform students objectively about school offerings and requirements",
    backstory="A reliable source of educational information with extensive experience in the school system."
)

# Define trigger phrases for Angel and Devil
angel_devil_triggers = [
    "I need the Angel and Devil to weigh in", "I'm not sure", "not sure leh",
    "both perspectives", "different opinions", "angel and devil",
    "good and bad", "pros and cons", "positive and negative"
]

# Define function to check if prompt is similar to trigger phrases
def is_similar_to_trigger(prompt, trigger_phrases):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that determines if sentences are similar in meaning."},
                {"role": "user", "content": f"Is the following sentence similar in meaning to any of these: {', '.join(trigger_phrases)}? \n\n Sentence: '{prompt}'"}
            ],
            temperature=0
        )
        answer = response.choices[0].message.content.strip().lower()
        return answer in ["yes", "true", "similar", "definitely"]
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return False

# Function to check if the prompt is informational
def is_informational_query(prompt):
    informational_keywords = ["program", "CCA", "school info", "subject", "facility", "details"]
    is_informational = any(keyword in prompt.lower() for keyword in informational_keywords)
    st.write(f"Prompt informational check: {is_informational}")
    return is_informational

# Enhanced function to get response type
def get_response_type(prompt):
    st.write(f"Evaluating response type for prompt: {prompt}")

    if is_similar_to_trigger(prompt, angel_devil_triggers):
        st.write("Response type set to: angel_and_devil")
        return "angel_and_devil"
    elif "ask student councillor" in prompt.lower() or is_informational_query(prompt):
        st.write("Response type set to: student_councillor")
        return "student_councillor"
    else:
        st.write("Defaulting to response type: student_councillor")
        return "student_councillor"

# Function to determine whether to invoke Angel and Devil
def should_invoke_angel_and_devil(prompt, trigger_phrases):
    return is_similar_to_trigger(prompt, trigger_phrases)

# Function to generate a smart reply from OpenAI with initial prompt if the query is vague
def generate_openai_response(agent_name, prompt):
    context_message = ("You are assisting a student with finding the right secondary school. "
                       "Keep responses focused on school recommendations. Use Singapore schools only. "
                       "List each recommendation as bullet points. Ask about their strengths, interests, and if they have any special programmes in mind.")

    # Check if the prompt is vague and prompt the user for more information if needed
    vague_prompts = ["how do I start?", "how to choose?", "help me find a school", "what should I do?"]
    if any(vague_prompt in prompt.lower() for vague_prompt in vague_prompts):
        return "Could you tell me a bit about your interests, strengths, or any preferences you have in a school? This will help me tailor my recommendations to suit you better."

    try:
        # Requesting response from OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are {agent_name}. {context_message}"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.7
        )

        # Extract the content from the response
        if response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                openai_response = choice.message.content.strip()
                print("OpenAI API response content:\n", openai_response)
                st.write("OpenAI API response content:", openai_response)
                return openai_response
            else:
                raise ValueError("Unexpected response structure: 'message' or 'content' missing.")
        else:
            raise ValueError("Unexpected response structure: 'choices' missing or empty.")

    except Exception as e:
        print(f"Error with OpenAI API for {agent_name}: {e}")
        st.write(f"Error with OpenAI API for {agent_name}: {e}")
        return "I'm having trouble generating a response right now. Please try again later."

from fuzzywuzzy import fuzz  # Import for partial string matching
import requests

# Function to retrieve transport information based on keywords
def get_transport_info(prompt):
    dataset_id = "c5b440d1-51c6-466c-bf91-0633266ab9c3"  # Corrected resource_id
    url = f"https://data.gov.sg/api/action/datastore_search?resource_id={dataset_id}&limit=360"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract destination from prompt
        school_name = prompt.split("to ")[1] if "to " in prompt else None
        if not school_name:
            return "Please specify a destination for transport information."

        # Filter with fuzzy matching
        transport_info = []
        for record in data.get("result", {}).get("records", []):
            record_school_name = record.get("school_name", "").lower()
            match_score = fuzz.partial_ratio(school_name.lower(), record_school_name)
            print(f"Matching '{school_name}' with '{record_school_name}': Score {match_score}")

            if match_score > 80:
                bus_info = record.get("bus_desc", "No specific bus info")
                mrt_info = record.get("mrt_desc", "No specific MRT info")
                print(f"Adding info: Bus: {bus_info}, MRT: {mrt_info}")
                transport_info.append(f"Bus routes: {bus_info}, MRT station: {mrt_info}")

        return "\n".join(transport_info) if transport_info else f"No transport information found for {school_name}."

    except Exception as e:
        print(f"Error retrieving data: {e}")
        return f"Failed to retrieve transport data: {e}"

# Function to search PSLE info
def search_psle_info(prompt):
    # Placeholder function for PSLE info search
    # Implement the actual logic to fetch PSLE info based on the prompt
    return "PSLE score ranges vary by school. Please refer to the MOE website for the most recent information."

# Enhanced transport-related keyword detection
def get_student_councillor_response(prompt):
    st.write(f"Student Councillor received prompt: {prompt}")
    additional_message = ("For more detailed information on recent PSLE score ranges, "
                          "please check the MOE SchoolFinder at this URL: "
                          "[MOE SchoolFinder](https://www.moe.gov.sg/schoolfinder?journey=Secondary%20school)")

    # Transport keyword detection with various permutations
    transport_keywords = [
        "bus to", "mrt to", "which bus", "which mrt", 
        "how to get to", "directions to", "what bus goes to", 
        "what mrt goes to", "bus route to", "mrt route to", 
        "transport to", "how do I get to", "nearest bus to", 
        "nearest mrt to"
    ]
    
    # Check if any transport-related keyword is in the prompt
    if any(keyword in prompt.lower() for keyword in transport_keywords):
        transport_info = get_transport_info(prompt)
        return f"{transport_info}\n\n{additional_message}"

    elif "school data" in prompt.lower():
        school_data = get_school_collection_data()
        st.write("Returning school data from Student Councillor")
        return f"{school_data}\n\n{additional_message}"
    
    elif "psle" in prompt.lower() or "scoring" in prompt.lower():
        response = search_psle_info(prompt)
        st.write("Returning PSLE info from Student Councillor")
        return f"{response}\n\n{additional_message}"
    
    else:
        general_response = generate_openai_response("Student Councillor", prompt)
        return f"{general_response}\n\n{additional_message}"

# Query for school collection data
def get_school_collection_data():
    collectionId = 457
    url = f"https://api-production.data.gov.sg/v2/public/api/collections/{collectionId}/metadata"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        st.write("School data successfully loaded:", data)
        return data
    except requests.RequestException as e:
        st.error(f"Failed to fetch school data: {e}")
        return {"error": "Failed to fetch data from OpenAPI."}

# Determine if Angel and Devil should weigh in on Student Councillor response
def angel_and_devil_weigh_in(prompt):
    """Trigger Angel and Devil responses if prompt meets criteria."""
    if should_invoke_angel_and_devil(prompt, angel_devil_triggers):
        st.write("Triggering Angel and Devil responses...")

        student_councillor_response = get_student_councillor_response(prompt)

        angel_prompt = f"The Student Councillor said: '{student_councillor_response}' Now provide your perspective."
        angel_response = generate_openai_response("Angel", angel_prompt)

        devil_prompt = (
            f"The Student Councillor said: '{student_councillor_response}', "
            f"and Angel added: '{angel_response}'. Now respond with your perspective."
        )
        devil_response = generate_openai_response("Devil", devil_prompt)

        st.session_state["messages"].append({"role": "Student Councillor Bot", "content": student_councillor_response})
        with st.chat_message("Student Councillor Bot"):
            st.markdown(student_councillor_response)

        st.session_state["messages"].append({"role": "Angel Bot", "content": angel_response})
        with st.chat_message("Angel Bot"):
            st.markdown(angel_response)

        st.session_state["messages"].append({"role": "Devil Bot", "content": devil_response})
        with st.chat_message("Devil Bot"):
            st.markdown(devil_response)
    else:
        # If not invoking Angel and Devil, just get the Student Councillor's response
        student_councillor_response = get_student_councillor_response(prompt)
        st.session_state["messages"].append({"role": "Student Councillor Bot", "content": student_councillor_response})
        with st.chat_message("Student Councillor Bot"):
            st.markdown(student_councillor_response)

# Main interaction function in Streamlit
if prompt := st.chat_input("How can I help you with your school search?"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response type
    response_type = get_response_type(prompt)
    if response_type == "angel_and_devil":
        angel_and_devil_weigh_in(prompt)
    else:
        # Default to Student Councillor
        student_councillor_response = get_student_councillor_response(prompt)
        st.session_state["messages"].append({"role": "Student Councillor Bot", "content": student_councillor_response})
        with st.chat_message("Student Councillor Bot"):
            st.markdown(student_councillor_response)

# Disclaimer section at the bottom of the page
with st.expander("IMPORTANT NOTICE"):
    st.write("""
    This web application is a prototype developed for educational purposes only. 
    The information provided here is NOT intended for real-world usage and should not 
    be relied upon for making any decisions, especially those related to financial, legal, 
    or healthcare matters.

    Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. 
    You assume full responsibility for how you use any generated output.

    Always consult with qualified professionals for accurate and personalised advice.
    """)
