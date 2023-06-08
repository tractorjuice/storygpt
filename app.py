# Importing required packages
from wardley_map import wardley
from github import Github
from streamlit_chat import message
from streamlit_ace import st_ace
import streamlit as st
import requests
import openai
import time
from time import sleep
import base64
# Importing the functions from the external file
from wardley_chatbot import get_chatgpt_response, update_chat, get_messages, get_owm_map

# Import RecurrentGPT
from recurrentgpt import RecurrentGPT
from human_simulator import Human
from sentence_transformers import SentenceTransformer
from utils import get_init, parse_instructions
import re

API_ENDPOINT = "https://api.onlinewardleymaps.com/v1/maps/fetch?id="
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
GITHUB = st.secrets["GITHUB"]
QUERY = "Suggest 3 questions you can answer about this Wardley Map, include any issues with this map?"
GITHUBREPO = "swardley/Research2022"
MODEL = "gpt-4"
map_id = None

# Dictionary of map IDs with user-friendly names
map_dict = {
    "Tea Shop": "QRXryFJ8Q1NxhbHKQL",   
    "Agriculture 2023 Research": "gQuu7Kby3yYveDngy2", 
    "AI & Entertainment": "1LSW3jTlx4u16T06di", 
    "Prompt Engineering": "mUJtoSmOfqlfXhNMJP",
    "Microsoft Fabric": "K4DjW1RdsbUWV8JzoP",
    "Fixed Penalty Notices": "gTTfD4r2mORudVFKge"
}

def reset_map():
    st.session_state['messages'] = []
    st.session_state['total_tokens_used'] = 0
    st.session_state['tokens_used'] = 0
    st.session_state['past'] = []
    st.session_state['generated'] = []
    st.session_state['disabled_buttons'] = []

# Build the semantic search model
embedder = SentenceTransformer('multi-qa-mpnet-base-cos-v1')

try:
    g = Github(GITHUB)
    repo = g.get_repo(GITHUBREPO)
except GithubException as e:
    st.error(f"An error occurred contacting GitHub: {e}")
    repo = None

if 'tokens_used' not in st.session_state:
    st.session_state['tokens_used'] = 0
    
if 'total_tokens_used' not in st.session_state:
    st.session_state['total_tokens_used'] = 0

if 'generated' not in st.session_state:
    st.session_state['generated'] = []
    
if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    
if 'map_text' not in st.session_state:
    st.session_state['map_text'] = []
    
if 'current_map_id' not in st.session_state:
    st.session_state['current_map_id'] = []

if 'disabled_buttons' not in st.session_state:
    st.session_state['disabled_buttons'] = []

# Get a list of files available in the GitHub repository    
if 'file_list' not in st.session_state:
    st.session_state.file_list = []
    contents = repo.get_contents("")
    while contents:
        file_item = contents.pop(0)
        if file_item.type == "dir":
            contents.extend(repo.get_contents(file_item.path))
        else:
            file_name = file_item.name
            if not file_name.isupper() and not file_name.startswith('.') and file_name.lower() != 'readme.md':
                st.session_state.file_list.append(file_item.path)

st.set_page_config(page_title="Chat with your Wardley Map", layout="wide")               

with st.sidebar:
    st.title("Chat with Map")
    st.divider()
    st.markdown("Developed by Mark Craddock](https://twitter.com/mcraddock)", unsafe_allow_html=True)
    st.markdown("Current Version: 1.1.0")
    st.markdown("Using GPT-4 API")
    st.divider()
    st.write(f"Total Tokens Used: {st.session_state['total_tokens_used']}")
    st.write(f"Total Cost: ${round(st.session_state['total_tokens_used'] * 0.06 / 1000, 2)}")
    st.divider()
    st.markdown("## Select Wardley Map") 

map_selection = st.sidebar.radio("Map Selection", ("Select from GitHub", "Select from List", "Enter Map ID"), help="Select GitHub to get a list of Simon Wardley's latest research.\n\nSelect from list to get predefined maps.\n\nSelect Enter Map ID to provide your own Onlinewardleymaps id", key="map_selection")

if map_selection == "Select from List":
    selected_name = st.sidebar.selectbox("Select Map", list(map_dict.keys()))
    map_id = map_dict[selected_name]
elif map_selection == "Select from GitHub":
    if 'file_list' in st.session_state:
        selected_file = st.sidebar.selectbox("Select a Map", st.session_state.file_list)
        file_item = repo.get_contents(selected_file)
        file_content = base64.b64decode(file_item.content).decode('utf-8')
        map_id = selected_file
        st.session_state['file_content'] = file_content
else:
    map_id = st.sidebar.text_input("Enter Map ID:", key="map_id_input")
    selected_name = map_id
    
if map_selection != "Select from GitHub":
    if st.session_state.get('current_map_id') != map_id:
        reset_map()
        del st.session_state['messages']
        st.session_state['current_map_id'] = map_id
        query = QUERY
        st.session_state['map_text'] = get_owm_map(map_id)
        st.session_state['messages'] = get_messages(st.session_state['map_text'])      

if map_selection == "Select from GitHub":
    if st.session_state.get('current_map_id') != map_id:
        reset_map()
        st.session_state['current_map_id'] = map_id
        query = QUERY
        st.session_state['map_text'] = st.session_state['file_content']
        st.session_state['messages'] = get_messages(st.session_state['map_text'])

# Display the map in the sidebar
if 'map_text' in st.session_state:
    with st.sidebar:
        title = "No Title"
        map_text = st.session_state['map_text']
        for line in map_text.split("\n"):
            if line.startswith("title"):
                title = line.split("title ")[1]
        if title:
            st.markdown(f"### {title}")

        # Get the Wardley Map
        map, map_plot = wardley(map=map_text)
        
        # Plot the Wardley Map:
        map_placeholder = st.empty()
        map_placeholder.pyplot(map_plot)

        # Display any warnings drawing the map
        if map.warnings:
            st.write("Warnings parsing and the drawing map")
            for map_message in map.warnings:
                st.warning(map_message)
         
        st.write("### Map Code")

        # Display code with editor        
        content = st_ace(value=st.session_state['map_text'], keybinding="vscode")
        
if not content == st.session_state['map_text']:
    st.session_state['map_text'] = content
    st.session_state['messages'] = get_messages(st.session_state['map_text'])
    st.experimental_rerun()

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("## Chat")
    query = st.text_input("Question: ", value=QUERY, key="input")
    query_button = st.button("Ask Question", key="querybutton", help="Submit your question")
    st.divider()
    if query_button and query:
        with st.spinner("Thinking... this can take a while..."):
            messages = st.session_state['messages']
            messages = update_chat(messages, "user", query)
            try:
                content, response = get_chatgpt_response(messages, MODEL)
                st.session_state.tokens_used = response.total_tokens
                st.session_state.total_tokens_used = st.session_state.total_tokens_used + st.session_state.tokens_used
                messages = update_chat(messages, "assistant", content)
                st.session_state.generated.append(content)
                st.session_state.past.append(query)
            except:
                st.error("GPT-4 Error")
            st.experimental_rerun()

with col2:
    st.markdown("## Structured Prompts")
    st.divider()
    if st.session_state["generated"]:
        for text in st.session_state["generated"]:
            sentences = text.strip().split("\n")
            for i, sentence in enumerate(sentences):
                stripped_sentence = sentence.strip()
                if stripped_sentence and stripped_sentence[0].isdigit():
                    st.write(stripped_sentence)
                    generated_index = st.session_state["generated"].index(text)
                    unique_key = f"{generated_index}-{i}"
                    if st.button(f"Ask follow up question", key=unique_key, disabled=unique_key in st.session_state.disabled_buttons):
                        st.session_state.disabled_buttons.append(unique_key)  # Add the button key to the disabled list
                        with st.spinner("thinking... this can take a while..."):
                            messages = st.session_state['messages']
                            messages = update_chat(messages, "user", stripped_sentence)
                            try:
                                # code that makes a request to the OpenAI API
                                content, response = get_chatgpt_response(messages, MODEL)
                                st.session_state.tokens_used = response.total_tokens
                                st.session_state.total_tokens_used = st.session_state.total_tokens_used + st.session_state.tokens_used
                                messages = update_chat(messages, "assistant", content)
                                st.session_state.past.append(stripped_sentence)
                                st.session_state.generated.append(content)
                            except Exception as e:
                                if isinstance(e, openai.error.RateLimitError):
                                    st.error("You've exceeded the API rate limit.")
                                elif isinstance(e, openai.error.APIError):
                                    st.error("An API error occurred.")
                                else:
                                    st.error("An unknown error occurred.")
                            except Exception as e:
                                # handle any other kind of exception
                                st.error(f"A GPT-4 error occurred: {e}")
                        st.experimental_rerun()

with col3:
    st.markdown("## Long-Term Memory")
    st.divider()
    if st.session_state['generated']:
        download_doc_str = []
        for i in range(len(st.session_state['generated'])):
            st.divider()
            st.write(st.session_state['generated'][i])

        for i in range(len(st.session_state['generated']) - 1, -1, -1):    
            download_doc_str.append(st.session_state["generated"][-(i+1)])

        if download_doc_str:
            download_doc_str = '\n'.join(download_doc_str)
            st.download_button('Download', download_doc_str)
            
with col1:
    if st.session_state['generated']:
        download_chat_str = []
        for i in range(len(st.session_state['generated']) - 1, -1, -1):  # Loop in reverse order
            message(st.session_state['generated'][i], is_user=False, key=str(i) + '_assistant', avatar_style="shapes", seed=25)
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="shapes", seed=20)     
            download_chat_str.append(st.session_state["generated"][i])
            download_chat_str.append(st.session_state["past"][i])

        if download_chat_str:
            download_chat_str = '\n'.join(download_chat_str)
            st.download_button('Download',download_chat_str)
