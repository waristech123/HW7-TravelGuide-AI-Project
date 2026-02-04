# 🧳 HW7 – AI-Powered Travel Guide
**Author:** Waris Hussain

---

1) Purpose

The **AI-Powered Travel Guide** is a Python application that generates a **personalized, family-friendly travel itinerary** based on user input such as destination, number of days, interests, and special requirements.

This project demonstrates how **AI can be used in a practical, real-world workflow** to assist users with planning and decision-making, rather than just answering questions.

---

2) AI & AI-Assisted Workflow

This project uses an **AI language model** to:

- Understand natural language user preferences
- Apply constraints and guardrails (e.g., kid-friendly, limited walking)
- Generate a structured, multi-day travel itinerary
- Return output in **strict JSON format** for validation and reliability

The AI acts as a **planning assistant**, converting user input into a usable, structured plan.

---

3) What the Code Does (High Level)

- Uses **Streamlit** to create a simple web interface
- Collects user inputs (destination, duration, interests, constraints)
- Sends a structured prompt to an AI model
- Validates the AI response using a predefined JSON schema
- Displays the itinerary in readable Markdown
- Generates a downloadable **PDF travel plan**

---

4) How to Run the Project

 Install Dependencies
Make sure Python is installed, then run:

```bash
pip install streamlit openai reportlab

Set API Key (Environment Variable)

export OPENAI_API_KEY="your_api_key_here"
⚠️ Do NOT hardcode API keys in the source file.

5)Run the Application

streamlit run Travel_Guide.py
Use the App
	•	Enter destination and number of travel days
	•	Select interests and preferences
	•	Add optional guardrails
	•	Generate itinerary
	•	Download the itinerary as a PDF

7)Security & Safe Sharing (Required)
This repository does NOT include:
	•	API keys
	•	Tokens
	•	Passwords
	•	.env files
	•	Personal or sensitive information
All secrets are handled using environment variables, making the repository safe for public sharing on GitHub.

8)Project Structure

HW7-TravelGuide-AI-Project/
├── README.md
└── Travel_Guide.py

9)Key Learning Outcomes
	•	Practical use of AI for real-world applications
	•	Structured AI prompting and output validation
	•	Safe handling of credentials
	•	Converting AI output into multiple formats (web + PDF)

10)Future Improvements
	•	Add map integration for locations
	•	Support hotel and restaurant recommendations
	•	Allow saving itineraries to a database
	•	Add multi-language support

📎 Notes
This project was developed as part of an AI coursework assignment to demonstrate responsible, practical, and secure use of AI in software workflows.






