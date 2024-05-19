import re, os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# gpt-3.5-turbo, gpt-4, and gpt-4-turbo-preview point to the latest model version
#MODEL = "gpt-3.5-turbo" # 4K, Sept 2021. Legacy. Currently points to gpt-3.5-turbo-0613.
#MODEL = "gpt-3.5-turbo-16k" # 16K, Sept 2021. Legacy. Snapshot of gpt-3.5-turbo from June 13th 2023. Will be deprecated on June 13, 2024
#MODEL = "gpt-3.5-turbo-1106" # 16K, Sept 2021. New Updated GPT 3.5 Turbo. The latest GPT-3.5 Turbo model with improved instruction following, JSON mode, reproducible outputs, parallel function calling, and more. Returns a maximum of 4,096 output tokens.
#MODEL = "gpt-4" # 8K, Sept 2021
#MODEL = "gpt-4-32k" # 32K, Sept 2021
#MODEL = "gpt-4-turbo-preview" # 128K, Apr 2023
#MODEL = "gpt-4-1106-preview" # 128K, Apr 2023
MODEL = "gpt-4o"

def get_api_response(content: str, max_tokens=None):
    chat = ChatOpenAI(
        openai_api_key=st.session_state.user_openai_api_key,
        model=MODEL,
        temperature=0.5,
        max_tokens=max_tokens,
        tags=["story-gpt", st.session_state.session_id],
    )
    response = None

    messages = [
        SystemMessage(content='You are a helpful and creative assistant for writing novels.'),
        HumanMessage(content=content)
    ]
    try:
        response = chat(messages)
    except:
        st.error("OpenAI Error")
    if response is not None:
        return response.content
    else:
        return "Error: response not found"

def get_content_between_a_b(a, b, text):
    return re.search(f"{a}(.*?)\n{b}", text, re.DOTALL).group(1).strip()

def get_init(init_text=None,text=None,response_file=None):
    if not init_text:
        response = get_api_response(text)

        if response_file:
            with open(response_file, 'a', encoding='utf-8') as f:
                f.write(f"Init output here:\n{response}\n\n")
    else:
        with open(init_text, 'r', encoding='utf-8') as f:
            response = f.read()

    paragraphs = {
        "name": "",
        "Outline": "",
        "Paragraph 1": "",
        "Paragraph 2": "",
        "Paragraph 3": "",
        "Summary": "",
        "Instruction 1": "",
        "Instruction 2": "",
        "Instruction 3": ""
    }

    paragraphs['name'] = get_content_between_a_b('Name:', 'Outline', response)
    paragraphs['Paragraph 1'] = get_content_between_a_b('Paragraph 1:', 'Paragraph 2:', response)
    paragraphs['Paragraph 2'] = get_content_between_a_b('Paragraph 2:', 'Paragraph 3:', response)
    paragraphs['Paragraph 3'] = get_content_between_a_b('Paragraph 3:', 'Summary', response)
    paragraphs['Summary'] = get_content_between_a_b('Summary:', 'Instruction 1', response)
    paragraphs['Instruction 1'] = get_content_between_a_b('Instruction 1:', 'Instruction 2', response)
    paragraphs['Instruction 2'] = get_content_between_a_b('Instruction 2:', 'Instruction 3', response)

    print(paragraphs)

    lines = response.splitlines()

    if lines[-1] != '\n' and lines[-1].startswith('Instruction 3'):
        paragraphs['Instruction 3'] = lines[-1][len("Instruction 3:"):]
    elif lines[-1] != '\n':
        paragraphs['Instruction 3'] = lines[-1]

    for line in lines:
        if line.startswith('Chapter'):
            paragraphs['Outline'] = get_content_between_a_b('Outline:', 'Chapter', response)
            break

    if paragraphs['Outline'] == '':
        paragraphs['Outline'] = get_content_between_a_b('Outline:', 'Paragraph', response)

    return paragraphs

def parse_instructions(instructions):
    output = ""
    for i in range(len(instructions)):
        output += f"{i+1}. {instructions[i]}\n"
    return output
