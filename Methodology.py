import streamlit as st

st.title("AI Chatbot Methodology")

st.write("""
### Flowchart Overview for Chatbot Methodology

This flowchart for the AI chatbot methodology includes several key steps that enable seamless user interactions with the Angel and Devil School Finder Chatbot.

1. **Agent Selection**  
   The chatbot determines which agent (Angel, Devil, or Student Councillor) will handle the user’s query. Each agent provides a unique response style, guiding the user toward relevant school information or decision-making advice.

2. **Information Retrieval**  
   Once the appropriate agent is selected, the chatbot retrieves relevant information, such as specific school details or PSLE scores. The chatbot may pull data from various sources, including the Ministry of Education’s PSLE resources or the Open Data API.  
   
   - **PSLE Score Explanation Scraping**  
     For queries related to PSLE scores, the chatbot uses **PyMuPDF** to extract specific explanations from the Ministry of Education’s PSLE informational PDF. By accessing this PDF, the chatbot retrieves official explanations on PSLE scoring, offering users accurate information directly from the source.

3. **Response Display**  
   The chatbot presents the retrieved information or advice to the user. This response could include details like PSLE scoring information, school programs, or recommendations based on personal interests and logistical factors.

This structured methodology ensures that the chatbot provides balanced, well-rounded responses to support students and parents in their school selection journey.

""")

# Add two-line spacing
st.write("\n\n")

# Display the image with a clickable link
st.markdown(
    """
    <p style="text-align: center;">
        <a href="https://drive.google.com/file/d/1d4ssuXBIZ1sbo5sP0hAkyAKHeUzXoZmJ/view?usp=drive_link" target="_blank">
            <img src="https://drive.google.com/uc?export=view&id=1d4ssuXBIZ1sbo5sP0hAkyAKHeUzXoZmJ" style="width:70%;"/>
        </a>
    </p>
    """,
    unsafe_allow_html=True
)
