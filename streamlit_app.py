import streamlit as st
from sentence_transformers import SentenceTransformer
from utils import get_init, parse_instructions
from human_simulator import Human
from recurrentgpt import RecurrentGPT

st.set_page_config(page_title="Wardley Map Novel", layout="wide") 

@st.cache_resource
def load_sentence_transformer_model():
    return SentenceTransformer('multi-qa-mpnet-base-cos-v1')

# Load the model only once
# Build the semantic search model
embedder = load_sentence_transformer_model()

if 'cache' not in st.session_state:
    st.session_state['cache'] = {}
    
if 'instruction1' not in st.session_state:
    st.session_state['instruction1'] = ""
    
if 'instruction2' not in st.session_state:
    st.session_state['instruction2'] = ""
    
if 'instruction3' not in st.session_state:
    st.session_state['instruction3'] = ""
    
if 'written_paras' not in st.session_state:
    st.session_state['written_paras'] = ""
    
if 'short_memory' not in st.session_state:
    st.session_state['short_memory'] = ""
    
if 'long_memory' not in st.session_state:
    st.session_state['long_memory'] = ""  
    

def init_prompt(novel_type, description):
    if description == "":
        description = ""
    else:
        description = " about " + description
    return f"""
Please write a {novel_type} novel{description} with 3 chapters. Follow the format below precisely:

Begin with the name of the novel.
Next, write an outline for the first chapter. The outline should describe the background and the beginning of the novel.
Write the first three paragraphs with their indication of the novel based on your outline. Write in a novelistic style and take your time to set the scene.
Write a summary that captures the key information of the three paragraphs.
Finally, write three different instructions for what to write next, each containing around five sentences. Each instruction should present a possible, interesting continuation of the story.
The output format should follow these guidelines:
Name: <name of the novel>
Outline: <outline for the first chapter>
Paragraph 1: <content for paragraph 1>
Paragraph 2: <content for paragraph 2>
Paragraph 3: <content for paragraph 3>
Summary: <content of summary>
Instruction 1: <content for instruction 1>
Instruction 2: <content for instruction 2>
Instruction 3: <content for instruction 3>

Make sure to be precise and follow the output format strictly.
"""

def init(novel_type, description):
    written_paras = ""
    if novel_type == "":
        novel_type = "Science Fiction"
    #cache = st.session_state['cache']
    # prepare first init
    
    init_text = init_prompt(novel_type, description)
    init_paragraphs = get_init(text=init_text)

    start_input_to_human = {
        'output_paragraph': init_paragraphs['Paragraph 3'],
        'input_paragraph': '\n\n'.join([init_paragraphs['Paragraph 1'], init_paragraphs['Paragraph 2']]),
        'output_memory': init_paragraphs['Summary'],
        "output_instruction": [init_paragraphs['Instruction 1'], init_paragraphs['Instruction 2'], init_paragraphs['Instruction 3']]
    }
    
    st.write("start_input_to_human")
    st.code(start_input_to_human)

    cache["start_input_to_human"] = start_input_to_human
    cache["init_paragraphs"] = init_paragraphs
    st.session_state['cache'] = cache

    written_paras = f"""Title: {init_paragraphs['name']}
Outline: {init_paragraphs['Outline']}
Paragraphs:
{start_input_to_human['input_paragraph']}"""

    long_memory = parse_instructions([init_paragraphs['Paragraph 1'], init_paragraphs['Paragraph 2']])
    return start_input_to_human['output_memory'], long_memory, written_paras, init_paragraphs['Instruction 1'], init_paragraphs['Instruction 2'], init_paragraphs['Instruction 3']

def step(short_memory, long_memory, instruction1, instruction2, instruction3, current_paras):
    cache = st.session_state['cache']
    if current_paras == "":
        return "", "", "", "", "", ""

    if "writer" not in cache:
        start_input_to_human = cache["start_input_to_human"]
        start_input_to_human['output_instruction'] = [
            instruction1, instruction2, instruction3]
        init_paragraphs = cache["init_paragraphs"]
        human = Human(input=start_input_to_human,
                      memory=None, embedder=embedder)
        human.step()
        start_short_memory = init_paragraphs['Summary']
        writer_start_input = human.output

        # Init writerGPT
        writer = RecurrentGPT(input=writer_start_input, short_memory=start_short_memory, long_memory=[
            init_paragraphs['Paragraph 1'], init_paragraphs['Paragraph 2']], memory_index=None, embedder=embedder)
        cache["writer"] = writer
        cache["human"] = human
        writer.step()
    else:
        human = cache["human"]
        writer = cache["writer"]
        output = writer.output
        output['output_memory'] = short_memory
        output['output_instruction'] = [
            instruction1, instruction2, instruction3]
        human.input = output
        human.step()
        writer.input = human.output
        writer.step()

    st.session_state['cache'] = cache
    long_memory = [[v] for v in writer.long_memory]
    return writer.output['output_memory'], long_memory, current_paras + '\n\n' + writer.output['input_paragraph'], human.output['output_instruction'], *writer.output['output_instruction']


def controled_step(short_memory, long_memory, selected_instruction, current_paras):
    if current_paras == "":
        return "", "", "", "", "", ""

    if "writer" not in st.session_state['cache']:
        cache = st.session_state['cache']
        start_input_to_human = cache["start_input_to_human"]
        start_input_to_human['output_instruction'] = selected_instruction
        init_paragraphs = cache["init_paragraphs"]
        human = Human(input=start_input_to_human,
                      memory=None, embedder=embedder)
        human.step_with_edit()
        start_short_memory = init_paragraphs['Summary']
        writer_start_input = human.output

        # Init writerGPT
        writer = RecurrentGPT(input=writer_start_input, short_memory=start_short_memory, long_memory=[
            init_paragraphs['Paragraph 1'], init_paragraphs['Paragraph 2']], memory_index=None, embedder=embedder)
        cache["writer"] = writer
        cache["human"] = human
        writer.step()
    else:
        human = cache["human"]
        writer = cache["writer"]
        output = writer.output
        output['output_memory'] = short_memory
        output['output_instruction'] = selected_instruction
        human.input = output
        human.step_with_edit()
        writer.input = human.output
        writer.step()
        
    cache = st.session_state['cache']
    return writer.output['output_memory'], parse_instructions(writer.long_memory), current_paras + '\n\n' + writer.output['input_paragraph'], *writer.output['output_instruction']


def on_select(instruction1, instruction2, instruction3, value):
    selected_plan = int(value.replace("Instruction ", ""))
    selected_plan = [instruction1, instruction2, instruction3][selected_plan-1]
    return selected_plan

cache = st.session_state['cache']
short_memory = st.session_state['short_memory']
long_memory = st.session_state['long_memory']
written_paras = st.session_state['written_paras']
instruction1 = st.session_state['instruction1']
instruction2 = st.session_state['instruction2']
instruction3 = st.session_state['instruction3']

tabs = st.sidebar.radio("Select Mode", ("Human-in-the-Loop", "Auto-Generation", ))
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
    instruction1 = st.text_area("Instruction 1 (editable)", value=instruction1, height=100, max_chars=500, key="instruction1", disabled=True)
    instruction2 = st.text_area("Instruction 2 (editable)", value=instruction2, height=100, max_chars=500, key="instruction2", disabled=True)
    instruction3 = st.text_area("Instruction 3 (editable)", value=instruction3, height=100, max_chars=500, key="instruction3", disabled=True)

    if st.button("Next Step"):
        short_memory, long_memory, written_paras, instruction1, instruction2, instruction3 = step(short_memory, long_memory, instruction1, instruction2, instruction3, written_paras)

else:
    novel_type = st.text_input("Novel Type", value="Science Fiction")
    description = st.text_input("Description")

    if st.button("Init Novel Generation"):
        short_memory, long_memory, written_paras, instruction1, instruction2, instruction3 = init(novel_type, description)

    written_paras = st.text_area("Written Paragraphs (editable)", value=written_paras, height=300, max_chars=2000)
    st.markdown("### Memory Module")
    short_memory = st.text_area("Short-Term Memory (editable)", height=100, max_chars=500, value=short_memory, key="short_memory")
    long_memory = st.text_area("Long-Term Memory (editable)", height=200, max_chars=1000, value=long_memory, key="long_memory")
    
    st.markdown("### Instruction Module")
    instruction1 = st.text_area("Instruction 1", height=100, max_chars=500, value=instruction1, key="selected_instruction1")
    instruction2 = st.text_area("Instruction 2", height=100, max_chars=500, value=instruction2, key="selected_instruction2")
    instruction3 = st.text_area("Instruction 3", height=100, max_chars=500, value=instruction3, key="selected_instruction3")

    selected_plan = st.radio("Instruction Selection", ["Instruction 1", "Instruction 2", "Instruction 3"])
    selected_instruction = on_select(instruction1, instruction2, instruction3, selected_plan)
    st.text_area("Selected Instruction (editable)", height=150, max_chars=1000, value=selected_instruction, key="selected_instruction")

    if st.button("Next Step"):
        st.session_state.instruction3short_memory, st.session_state.instruction3long_memory, st.session_state.instruction3written_paras, st.session_state.instruction3instruction1, st.session_state.instruction3instruction2, st.session_state.instruction3 = controled_step(short_memory, long_memory, selected_instruction, written_paras)
