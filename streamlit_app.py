import streamlit as st
from sentence_transformers import SentenceTransformer
from utils import get_init, parse_instructions
from human_simulator import Human
from recurrentgpt import RecurrentGPT

# Build the semantic search model
embedder = SentenceTransformer('multi-qa-mpnet-base-cos-v1')

CACHE = {}

def init_prompt(novel_type, description):
    if description == "":
        description = ""
    else:
        description = " about " + description
    return f"""
Please write a {novel_type} novel{description} with 50 chapters. Follow the format below precisely:
...
"""

def init(novel_type, description):
    if novel_type == "":
        novel_type = "Science Fiction"
    global CACHE
    # prepare first init
    init_text = init_prompt(novel_type, description)
    init_paragraphs = get_init(text=init_text)

    start_input_to_human = {
        'output_paragraph': init_paragraphs['Paragraph 3'],
        'input_paragraph': '\n\n'.join([init_paragraphs['Paragraph 1'], init_paragraphs['Paragraph 2']]),
        'output_memory': init_paragraphs['Summary'],
        "output_instruction": [init_paragraphs['Instruction 1'], init_paragraphs['Instruction 2'], init_paragraphs['Instruction 3']]
    }

    CACHE["start_input_to_human"] = start_input_to_human
    CACHE["init_paragraphs"] = init_paragraphs

    written_paras = f"""Title: {init_paragraphs['name']}
Outline: {init_paragraphs['Outline']}
Paragraphs:
{start_input_to_human['input_paragraph']}"""

    long_memory = parse_instructions([init_paragraphs['Paragraph 1'], init_paragraphs['Paragraph 2']])
    return start_input_to_human['output_memory'], long_memory, written_paras, init_paragraphs['Instruction 1'], init_paragraphs['Instruction 2'], init_paragraphs['Instruction 3']

def step(short_memory, long_memory, instruction1, instruction2, instruction3, current_paras):
    if current_paras == "":
        return "", "", "", "", "", ""

    if "writer" not in CACHE:
        start_input_to_human = CACHE["start_input_to_human"]
        start_input_to_human['output_instruction'] = [
            instruction1, instruction2, instruction3]
        init_paragraphs = CACHE["init_paragraphs"]
        human = Human(input=start_input_to_human,
                      memory=None, embedder=embedder)
        human.step()
        start_short_memory = init_paragraphs['Summary']
        writer_start_input = human.output

        # Init writerGPT
        writer = RecurrentGPT(input=writer_start_input, short_memory=start_short_memory, long_memory=[
            init_paragraphs['Paragraph 1'], init_paragraphs['Paragraph 2']], memory_index=None, embedder=embedder)
        CACHE["writer"] = writer
        CACHE["human"] = human
        writer.step()
    else:
        human = CACHE["human"]
        writer = CACHE["writer"]
        output = writer.output
        output['output_memory'] = short_memory
        output['output_instruction'] = [
            instruction1, instruction2, instruction3]
        human.input = output
        human.step()
        writer.input = human.output
        writer.step()

    long_memory = [[v] for v in writer.long_memory]
    return writer.output['output_memory'], long_memory, current_paras + '\n\n' + writer.output['input_paragraph'], human.output['output_instruction'], *writer.output['output_instruction']


def controled_step(short_memory, long_memory, selected_instruction, current_paras):
    if current_paras == "":
        return "", "", "", "", "", ""

    if "writer" not in CACHE:
        start_input_to_human = CACHE["start_input_to_human"]
        start_input_to_human['output_instruction'] = selected_instruction
        init_paragraphs = CACHE["init_paragraphs"]
        human = Human(input=start_input_to_human,
                      memory=None, embedder=embedder)
        human.step_with_edit()
        start_short_memory = init_paragraphs['Summary']
        writer_start_input = human.output

        # Init writerGPT
        writer = RecurrentGPT(input=writer_start_input, short_memory=start_short_memory, long_memory=[
            init_paragraphs['Paragraph 1'], init_paragraphs['Paragraph 2']], memory_index=None, embedder=embedder)
        CACHE["writer"] = writer
        CACHE["human"] = human
        writer.step()
    else:
        human = CACHE["human"]
        writer = CACHE["writer"]
        output = writer.output
        output['output_memory'] = short_memory
        output['output_instruction'] = selected_instruction
        human.input = output
        human.step_with_edit()
        writer.input = human.output
        writer.step()

    return writer.output['output_memory'], parse_instructions(writer.long_memory), current_paras + '\n\n' + writer.output['input_paragraph'], *writer.output['output_instruction']


def on_select(instruction1, instruction2, instruction3, value):
    selected_plan = int(value.replace("Instruction ", ""))
    selected_plan = [instruction1, instruction2, instruction3][selected_plan-1]
    return selected_plan


st.title("RecurrentGPT")

tabs = st.sidebar.radio("Select Mode", ("Auto-Generation", "Human-in-the-Loop"))

written_paras = ""

if tabs == "Auto-Generation":
    novel_type = st.text_input("Novel Type", value="Science Fiction")
    description = st.text_input("Description")

    if st.button("Init Novel Generation"):
        short_memory, long_memory, written_paras, instruction1, instruction2, instruction3 = init(novel_type, description)

    st.text_area("Written Paragraphs (editable)", value=written_paras, height=300, max_chars=2000)
    st.markdown("### Memory Module")
    short_memory = st.text_area("Short-Term Memory (editable)", height=100, max_chars=500)
    long_memory = st.text_area("Long-Term Memory (editable)", height=200, max_chars=1000)
    st.markdown("### Instruction Module")
    instruction1 = st.text_area("Instruction 1 (editable)", height=100, max_chars=500)
    instruction2 = st.text_area("Instruction 2 (editable)", height=100, max_chars=500)
    instruction3 = st.text_area("Instruction 3 (editable)", height=100, max_chars=500)

    if st.button("Next Step"):
        short_memory, long_memory, written_paras, instruction1, instruction2, instruction3 = step(short_memory, long_memory, instruction1, instruction2, instruction3, written_paras)


else:
    novel_type = st.text_input("Novel Type", value="Science Fiction")
    description = st.text_input("Description")

    if st.button("Init Novel Generation"):
        short_memory, long_memory, written_paras, instruction1, instruction2, instruction3 = init(novel_type, description)

    st.text_area("Written Paragraphs (editable)", value=written_paras, height=300, max_chars=2000)
    st.markdown("### Memory Module")
    short_memory = st.text_area("Short-Term Memory (editable)", height=100, max_chars=500)
    long_memory = st.text_area("Long-Term Memory (editable)", height=200, max_chars=1000)
    st.markdown("### Instruction Module")
    instruction1 = st.text_area("Instruction 1", height=100, max_chars=500, value=instruction1, key="instruction1", disabled=True)
    instruction2 = st.text_area("Instruction 2", height=100, max_chars=500, value=instruction2, key="instruction2", disabled=True)
    instruction3 = st.text_area("Instruction 3", height=100, max_chars=500, value=instruction3, key="instruction3", disabled=True)

    selected_plan = st.radio("Instruction Selection", ["Instruction 1", "Instruction 2", "Instruction 3"])
    selected_instruction = st.text_area("Selected Instruction (editable)", height=150, max_chars=1000)

    if st.button("Next Step"):
        short_memory, long_memory, written_paras, instruction1, instruction2, instruction3 = controled_step(short_memory, long_memory, selected_instruction, written_paras)

    selected_instruction = on_select(instruction1, instruction2, instruction3, selected_plan)

    st.text_area("Selected Instruction (editable)", value=selected_instruction, height=150, max_chars=1000)
