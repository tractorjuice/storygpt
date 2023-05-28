import streamlit as st
import requests
import openai

def get_initial_message(map_id):
    url = f"https://api.onlinewardleymaps.com/v1/maps/fetch?id={map_id}"
    
    try:
        response = requests.get(url)
        
        # Check if the response status code is 200 (successful)
        if response.status_code == 200:
            map_data = response.json()
            
            # Check if the expected data is present in the response JSON
            if "text" in map_data:
                map_text = map_data["text"]
                st.session_state['map_text'] = map_text
            else:
                st.warning("The response JSON does not contain the expected 'text' key.")
                return []
        else:
            st.warning(f"The API request failed with status code {response.status_code}.")
            return []
    
    except requests.exceptions.RequestException as e:
        st.warning(f"An error occurred while making the API request: {e}")
        return []
    
    messages = [
        {
            "role": "system",
            "content": f"""
            As a chatbot, analyze the provided Wardley Map and offer insights and recommendations based on its components.
             
            Wardley Map Definition using RegEx:

            RegEx	Description
            (pioneers|settlers|townplanners)(\\s*\\[)(\\d+(?:\\.\\d{1,})*)(\\,\\s*)(\\d+(?:\\.\\d{1,})*)(\\,\\s*)(\\d+(?:\\.\\d{1,})*)(\\,\\s*)(\\d+(?:\\.\\d{1,}))(\\])	Identifies one of three keywords (pioneers, settlers, townplanners) followed by a space, then four decimal numbers (integers or floats) enclosed in square brackets, each separated by a comma.
            (url)(\\s*[a-zA-Z0-9\\s*]+)(\\s*\\[)(\\s*[-+\'"/;:.#a-zA-Z0-9\\s*]+)(\\])	Identifies the keyword "url" followed by a space and a string, and then a second string enclosed in square brackets.
            (url)(\\s*\\()(\\s*[-+\'"/;:a-zA-Z0-9\\s*]+)(\\))	Identifies the keyword "url" followed by a space and an open parenthesis, then a string enclosed in parentheses.
            (\\s*\\()([-+(build|buy|outsource|ecosystem|market)\\s*]+)(\\))	Identifies one of five keywords (build, buy, outsource, ecosystem, market) enclosed in parentheses.
            (\\/\\/.*$)	Identifies a line comment, which starts with "//" and continues until the end of the line.
            (y-axis|evolution|note|anchor|annotations|annotation|component|ecosystem|market|submap|title|style|outsource|build|product|buy|pipeline)(\\s*[-+\'";a-zA-Z0-9\\s*]+)	Identifies one of 15 keywords followed by a space and then a string.
            (evolve)(\\s*[a-zA-Z0-9\\s*]+)(\\d+(?:\\.\\d{1,})*)	Identifies the evolution of a component within the Wardley Map.
            (label)(\\s*\\[)(-*\\d+)(\\,\\s*)(-*\\d+)(\\])	Identifies the relative location for the labelling components within the Wardley Map.
            (inertia)	Identifies inertia within the Wardley Map.
            (\\[*)(\\[)(\\d+(?:\\.\\d{1,})*)(\\,\\s*)(\\d+(?:\\.\\d{1,}))(\\])(\\]*)	Identifies the coordinates for the location within the Wardley Map.
            (\\s*[a-zA-Z0-9\\s*]+)(\\-\\>)(\\s*[a-zA-Z0-9\\s*]+)	Identifies links between components.
            
            Suggestions:
            Request the Wardley Map for analysis
            Explain the analysis process for a Wardley Map
            Discuss the key insights derived from the map
            Provide recommendations based on the analysis
            Offer guidance for potential improvements or adjustments to the map
            WARDLEY MAP: {map_text}
            """
        },
        {
            "role": "user",
            "content": "{question} Output as markdown"
        },
        {
            "role": "assistant",
            "content": """
            Here is a list of general questions that you could consider asking while examining any Wardley Map:
            1. What is the focus of this map - a specific industry, business process, or company's value chain?
            2. What are the main user needs the map is addressing, and have all relevant user needs been identified?
            3. Are the components correctly placed within the map based on their evolutions (Genesis, Custom Built, Product/Rental, Commodity)?
            4. What linkages exist between the components and how do they interact within the value chain?
            5. Can you identify any market trends or competitor activities that could impact the positioning of the components?
            6. Are there any potential inefficiencies or improvements that could be made in the value chain depicted in the map?
            7. How does your organization take advantage of upcoming opportunities or mitigate risks, considering the layout and components' evolutions on the map?
            8. Are there any areas where innovation or disruption could significantly alter the landscape represented in the map?
            It is essential to provide the actual Wardley Map in question to provide a more accurate, in-depth analysis of specific components or insights tailored to your map.
            """
        }
    ]
    return messages

def get_owm_map(map_id):
    url = f"https://api.onlinewardleymaps.com/v1/maps/fetch?id={map_id}"
    
    try:
        response = requests.get(url)
        
        # Check if the response status code is 200 (successful)
        if response.status_code == 200:
            map_data = response.json()
            
            # Check if the expected data is present in the response JSON
            if "text" in map_data:
                map_text = map_data["text"]
            else:
                st.warning("The response JSON does not contain the expected 'text' key.")
                return []
        else:
            st.warning(f"The API request failed with status code {response.status_code}.")
            return []
    
    except requests.exceptions.RequestException as e:
        st.warning(f"An error occurred while making the API request: {e}")
        return []
    
    return(map_text)

def get_messages(map_text):
    messages = [
        {
            "role": "system",
            "content": f"""
            As a chatbot, analyze the provided Wardley Map and offer insights and recommendations based on its components.
             
            Wardley Map Definition using RegEx:

            RegEx	Description
            (pioneers|settlers|townplanners)(\\s*\\[)(\\d+(?:\\.\\d{1,})*)(\\,\\s*)(\\d+(?:\\.\\d{1,})*)(\\,\\s*)(\\d+(?:\\.\\d{1,})*)(\\,\\s*)(\\d+(?:\\.\\d{1,}))(\\])	Identifies one of three keywords (pioneers, settlers, townplanners) followed by a space, then four decimal numbers (integers or floats) enclosed in square brackets, each separated by a comma.
            (url)(\\s*[a-zA-Z0-9\\s*]+)(\\s*\\[)(\\s*[-+\'"/;:.#a-zA-Z0-9\\s*]+)(\\])	Identifies the keyword "url" followed by a space and a string, and then a second string enclosed in square brackets.
            (url)(\\s*\\()(\\s*[-+\'"/;:a-zA-Z0-9\\s*]+)(\\))	Identifies the keyword "url" followed by a space and an open parenthesis, then a string enclosed in parentheses.
            (\\s*\\()([-+(build|buy|outsource|ecosystem|market)\\s*]+)(\\))	Identifies one of five keywords (build, buy, outsource, ecosystem, market) enclosed in parentheses.
            (\\/\\/.*$)	Identifies a line comment, which starts with "//" and continues until the end of the line.
            (y-axis|evolution|note|anchor|annotations|annotation|component|ecosystem|market|submap|title|style|outsource|build|product|buy|pipeline)(\\s*[-+\'";a-zA-Z0-9\\s*]+)	Identifies one of 15 keywords followed by a space and then a string.
            (evolve)(\\s*[a-zA-Z0-9\\s*]+)(\\d+(?:\\.\\d{1,})*)	Identifies the evolution of a component within the Wardley Map.
            (label)(\\s*\\[)(-*\\d+)(\\,\\s*)(-*\\d+)(\\])	Identifies the relative location for the labelling components within the Wardley Map.
            (inertia)	Identifies inertia within the Wardley Map.
            (\\[*)(\\[)(\\d+(?:\\.\\d{1,})*)(\\,\\s*)(\\d+(?:\\.\\d{1,}))(\\])(\\]*)	Identifies the coordinates for the location within the Wardley Map.
            (\\s*[a-zA-Z0-9\\s*]+)(\\-\\>)(\\s*[a-zA-Z0-9\\s*]+)	Identifies links between components.
            
            Suggestions:
            Request the Wardley Map for analysis
            Explain the analysis process for a Wardley Map
            Discuss the key insights derived from the map
            Provide recommendations based on the analysis
            Offer guidance for potential improvements or adjustments to the map
            WARDLEY MAP: {map_text}
            """
        },
        {
            "role": "user",
            "content": "{question} Output as markdown"
        },
        {
            "role": "assistant",
            "content": """
            Here is a list of general questions that you could consider asking while examining any Wardley Map:
            1. What is the focus of this map - a specific industry, business process, or company's value chain?
            2. What are the main user needs the map is addressing, and have all relevant user needs been identified?
            3. Are the components correctly placed within the map based on their evolutions (Genesis, Custom Built, Product/Rental, Commodity)?
            4. What linkages exist between the components and how do they interact within the value chain?
            5. Can you identify any market trends or competitor activities that could impact the positioning of the components?
            6. Are there any potential inefficiencies or improvements that could be made in the value chain depicted in the map?
            7. How does your organization take advantage of upcoming opportunities or mitigate risks, considering the layout and components' evolutions on the map?
            8. Are there any areas where innovation or disruption could significantly alter the landscape represented in the map?
            It is essential to provide the actual Wardley Map in question to provide a more accurate, in-depth analysis of specific components or insights tailored to your map.
            """
        }
    ]
    return messages

def get_chatgpt_response(messages, model):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    content = response['choices'][0]['message']['content']
    return content, response  # Return the response along with the content
  
def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages
