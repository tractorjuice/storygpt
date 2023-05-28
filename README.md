# Wardley Insight Report

This Streamlit application allows users to interact with a chatbot trained on GPT-4 to analyze and provide insights on a given Wardley Map. Users can ask questions and receive insights on various aspects of the map, such as component relationships, market trends, and potential improvements. Producing a final report of the insights

## Features

- Retrieve a Wardley Map based on its ID.
- Fetch a Wardley Map based on a predefined list of IDs.
- Get a Wardley Map from a GitHub repository
- Interact with a GPT-4 based chatbot to ask questions and receive insights about the Wardley Map.
- Display generated responses from the chatbot.
- Download chat transcripts and generated documents as separate files.

## Requirements

- Python 3.7+
- Streamlit
- OpenAI Python package
- Requests

## Installation

1. Clone the repository:

`git clone https://github.com/yourusername/wardley-insight-report.git`

2. Install the required dependencies:

`.pip install -r requirements.txt`

3. Set up your OpenAI API key as a secret:

Create a file named `.streamlit/secrets.toml` in your project directory and add your OpenAI API key:

[general]
`.OPENAI_API_KEY = "your_openai_api_key_here"`

4. Run the Streamlit application:

`.streamlit run app.py`

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://wardleyinsightreport.streamlit.app/)

## Usage
Enter the ID of a Wardley Map you would like to analyze.

The map's content will be displayed in the sidebar.

Type your question in the "Question" input box.

The chatbot will provide its response in the chat window.

Generated responses are displayed in reverse order in a separate column, along with buttons for additional actions.

Download the chat transcript or the generated document using the download buttons provided.

## Contributing
Feel free to submit issues and pull requests to improve the application. For major changes, please open an issue first to discuss what you would like to change.
