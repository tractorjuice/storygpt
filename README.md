# StoryGPT

This Streamlit application allows users to interact with a chatbot trained on GPT-4 to create a story.

## Features

- Enables manual creation of stories using ChatGPT and LangChain

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
Enter the description of the story
Initialise the story
Select the preferred paragraph to generate a section for your story.

## Contributing
Feel free to submit issues and pull requests to improve the application. For major changes, please open an issue first to discuss what you would like to change.

## Source
Inspired by RecurrentGPT https://github.com/aiwaves-cn/RecurrentGPT
