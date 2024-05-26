# StoryGPT - A Novel Writing Assistant

StoryGPT is a Streamlit-based application designed to assist users in generating novel-length stories using GPT models. It offers both auto-generation and human-in-the-loop modes, leveraging the capabilities of Sentence Transformers and OpenAI's GPT models.

## Features

- **Auto-Generation Mode:** Automatically generate novel content based on user inputs.
- **Human-in-the-Loop Mode:** Allow users to interact and guide the story generation process.
- **Memory Modules:** Utilize short-term and long-term memory to maintain context throughout the story.
- **Instruction Modules:** Provide multiple instructions for the next part of the story, allowing users to choose the direction.

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/storygpt.git
    cd storygpt
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables:**
    Create a `.streamlit/secrets.toml` file with your API keys:
    ```toml
    [secrets]
    OPENAI_API_KEY = "your_openai_api_key"
    GROQ_API_KEY = "your_groq_api_key"
    LANGCHAIN_PROJECT = "your_langchain_project"
    LANGCHAIN_API_KEY = "your_langchain_api_key"
    ```

## Usage

1. **Run the Streamlit App:**
    ```bash
    streamlit run app.py
    ```

2. **Access the Application:**
    Open your browser and go to `http://localhost:8501`.

## How to Use

### Auto-Generation Mode

1. Enter the novel type and a brief description.
2. Click "Initialise Novel Generation" to start.
3. Edit the generated paragraphs, short-term memory, long-term memory, and instructions as needed.
4. Click "Next Step" to generate the next part of the story.

### Human-in-the-Loop Mode

1. Enter the novel type and a brief description.
2. Click "Initialise Novel Generation" to start.
3. Review the generated paragraphs and memory modules.
4. Choose from the provided instructions for the next part of the story.
5. Click "Next Step" to generate the next part of the story.

## Customization

### Custom CSS

The application includes custom CSS for styling buttons. You can modify the `custom_css_styling` variable in `app.py` to change the button styles.

### Changing the GPT Model

By default, the application uses `gpt-3.5-turbo-16k-0613`. You can change this by modifying the `MODEL` variable in `utils.py`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Sentence Transformers](https://www.sbert.net/)
- [OpenAI](https://www.openai.com/)
- [LangChain](https://langchain.com/)

## Contact

Developed by [Mark Craddock](https://twitter.com/mcraddock). For questions or feedback, reach out on Twitter or open an issue on GitHub.
