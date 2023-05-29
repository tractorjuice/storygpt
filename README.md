# StoryGPT

This Streamlit application allows users to interact with a chatbot trained on GPT-4 to create a story.

## Features

- 

## Requirements

- Python 3.7+
- Streamlit
- OpenAI Python package
- Requests

## Installation

1. Clone the repository:

`git clone https://github.com/yourusername/wardley-insight-report.git`

2. Install the required dependencies:

`pip install -r requirements.txt`

3. Set up your OpenAI API key as a secret:

Add your OpenAI API Key to the Streamlit secrets within the administration interface:

`OPENAI_API_KEY = "your_openai_api_key_here"`

4. Run the Streamlit application:

`.streamlit run app.py`

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://storygpt.streamlit.app/)

## Usage
Enter the ID of a Wardley Map you would like to analyze.

The map's content will be displayed in the sidebar.

Type your question in the "Question" input box.

The chatbot will provide its response in the chat window.

Generated responses are displayed in reverse order in a separate column, along with buttons for additional actions.

Download the chat transcript or the generated document using the download buttons provided.

## Contributing
Feel free to submit issues and pull requests to improve the application. For major changes, please open an issue first to discuss what you would like to change.
