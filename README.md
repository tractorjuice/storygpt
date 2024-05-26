# Story Generator

Welcome to the Story Generator, a novel-writing assistant that uses advanced AI models to help you generate and continue a story. This application leverages OpenAI's GPT models and the Sentence Transformers library to create and maintain a coherent narrative over long contexts.

## Features

- Generate an initial novel structure and content.
- Continue the story with automated or human-in-the-loop modes.
- Maintain short-term and long-term memory of the narrative to ensure coherence.
- Interactive UI built with Streamlit for easy story development.

## Setup

### Prerequisites

- Python 3.7 or higher
- Streamlit
- OpenAI API key
- Sentence Transformers library
- Langchain library

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/story-generator.git
   cd story-generator

2. Install the required dependencies:
```bash
   pip install -r requirements.txt

Set up environment variables:

Create a `.env` file in the root directory and add your OpenAI API key and other necessary keys:

```env
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_PROJECT=your_langchain_project
LANGCHAIN_API_KEY=your_langchain_api_key





## Usage

### Initialize the Story

1. Enter the novel type and description.
2. Click on "Initialise Novel Generation" to generate the initial structure and content.

### Modes

- **Auto-Generation**: The AI generates the next part of the story automatically.
- **Human-in-the-Loop**: You can interact with the generated content, make edits, and guide the story.

### Human-in-the-Loop Mode

1. **Instructions**: View and edit the generated instructions.
2. **Memory Module**: Edit short-term and long-term memory to maintain context.
3. **Next Step**: Select the next step, edit instructions if necessary, and proceed.

## Code Overview

### app.py

Main Streamlit app file. Handles UI and user interactions, initializes the story, and processes steps for both auto-generation and human-in-the-loop modes.

### utils.py

Utility functions for interacting with the OpenAI API, parsing responses, and managing content.

### recurrentgpt.py

Defines the `RecurrentGPT` class which interacts with the GPT model to generate and continue story content. Manages short-term and long-term memory.

### human_simulator.py

Defines the `Human` class which simulates human input in the story generation process. Handles extending paragraphs and revising plans.


## Examples

### Initialize a Novel

1. Enter "Science Fiction" as the novel type.
2. Enter "A journey through space" as the description.
3. Click "Initialise Novel Generation".

### Continue the Story

1. In Auto-Generation mode, click "Next Step" to automatically generate the next part.
2. In Human-in-the-Loop mode, select and edit the instructions, update memories, and click "Next Step".

## License

This project is licensed under the MIT License.
