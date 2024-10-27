import streamlit as st

st.title("About Us")

st.write("""
## Welcome to the Angel and Devil School Finder Chatbot project! (AN ASSIGNMENT, ROUGH ALL AROUND THE EDGES)

### Project Scope and Objectives
This PROTOTPYE AND NOT FOR PUBLIC chatbot was developed as a PROJECT/ASSIGNMENT to assist students and parents in navigating the process of choosing a secondary school by providing comprehensive, multi-perspective insights. The main goal is to offer a balanced view through three distinct agents:
1. **Angel** - A friendly, encouraging agent that highlights schools aligned with the student’s interests and aspirations.
2. **Devil** - A pragmatic and realistic agent that considers practical aspects like distance, academic fit, and logistics.
3. **Student Councillor** - A neutral and factual agent who provides specific school-related information, such as programs, co-curricular activities (CCAs), and more.

Through this chatbot, users can explore options and make more informed school choices, balancing both passion and practicality.

### Features
- **Three-Agent System**: Each agent offers a unique perspective, allowing students to weigh different aspects before making a decision.
- **Interactive Q&A**: Users can interact with the agents by asking school-related questions, with the ability to switch between practical guidance (Devil), encouraging advice (Angel), and factual information (Student Councillor).
- **Personalised Recommendations**: Based on user queries, the chatbot provides a tailored list of school options, factoring in the user’s preferences and needs.

### Data Sources
- **Singapore Open Data API**: School data, including general information and program offerings, is sourced from the Singapore Open Data API, ensuring accurate and up-to-date information.
- **PSLE Achievement Levels*: Explanation on Achievement Levels as new PSLE scoring. Source: https://www.moe.gov.sg/microsites/psle-fsbb/assets/infographics/new-psle-scoring-system/psle-infosheet-english.pdf.

### Technology Stack
The app leverages:
- **Streamlit**: Provides a user-friendly interface for the chatbot.
- **ChromaDB (In-Memory)**: An in-memory storage solution to avoid SQLite limitations.
- **CrewAI**: An agent-based framework that powers the Angel, Devil, and Student Councillor personas, enabling nuanced responses to user inquiries.
- **PyMuPDF**: For extracting and presenting text content from Ministry of Education’s PSLE resources PDF.

This School Finder Chatbot aims to make the school selection process insightful and accessible, promoting informed decisions through a blend of empathy, realism, and reliable data.
""")
