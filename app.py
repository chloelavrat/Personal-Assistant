# ------------------------------------------------------------------------------
# ModularMinds App
# ----------------
#
# This Streamlit app allows you to use LLMs with differents personality profiles.
# This work is based on LamaCPP
#
# The page and the model integration has been developed by Azerty-Labs
# 
# <Copyright 2023 - Azerty-Labs>
# ------------------------------------------------------------------------------
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_chat import message
from hugchat import hugchat
# ------------------------------------------------------------------------------
def generate_response(prompt, chatbot):
    response = chatbot.chat(prompt)
    return response

def get_text():
    input_text = st.text_input("Input window", key="text", on_change=clear_text)    
    return st.session_state["temp"]

def clear_text():
    st.session_state["temp"] = st.session_state["text"]
    st.session_state["text"] = ""
# ------------------------------------------------------------------------------
def main():
    # Set up page
    st.set_page_config(
        page_title=st.secrets["page"]["page_title"],
        page_icon=st.secrets["page"]["page_icon"],
        layout=st.secrets["page"]["layout"])
    st.markdown(st.secrets["page"]["hide_menu_style"], unsafe_allow_html=True)
    st.markdown(st.secrets["page"]["footer"],unsafe_allow_html=True)

    # Header
    st.image("./assets/image/banner.png")
    st.markdown(open("./assets/text/introduction.md", 'r').read(), unsafe_allow_html=True)
    st.markdown("""---""") 

    # Session State Initialization
    if "chatID" not in st.session_state:
        chatbot = hugchat.ChatBot(cookie_path="./assets/cookies.json")
        #id = chatbot.new_conversation()
        #chatbot.change_conversation(id)
        st.session_state["startUp"] = id
    if "temp" not in st.session_state:
        st.session_state["temp"] = ""
    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["I'm Synthia, How may I help you?"]
    ## past stores User's questions
    if 'past' not in st.session_state:
        st.session_state['past'] =  [None]

    response_container = st.container()
    colored_header(label='', description='', color_name='gray-100')
    input_container = st.container()
    
    with input_container:
        user_input = get_text()

    with response_container:
        if user_input and st.session_state["startUp"]:
            response = generate_response(user_input, chatbot)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(response)
            
        if st.session_state['generated']:
            for i in range(len(st.session_state['generated'])):
                if st.session_state['past'][i] != None:
                    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="lorelei-neutral", seed=15)
                message(st.session_state["generated"][i], key=str(i), avatar_style="lorelei", seed=7)

if __name__ == "__main__":
    main()