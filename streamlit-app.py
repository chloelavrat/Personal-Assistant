import os
import json
import yt_dlp
import streamlit as st
import whisper
from hugchat import hugchat
from hugchat.login import Login
from prepromps import preprompts

# Define the cookie path directory
COOKIE_PATH_DIR = "./cookies/"
COOKIE_FILE_PATH = os.path.join(COOKIE_PATH_DIR, "cookies.json")

# Ensure the cookie directory exists
if not os.path.exists(COOKIE_PATH_DIR):
    os.makedirs(COOKIE_PATH_DIR)

model = whisper.load_model("base")


def authenticate(email: str, password: str):
    """
    Authenticate user and return cookies.
    """
    sign = Login(email, password)
    cookies = sign.login(cookie_dir_path=COOKIE_PATH_DIR, save_cookies=True)
    return cookies.get_dict()


def load_cookies():
    """
    Load cookies from file if they exist.
    """
    if os.path.exists(COOKIE_FILE_PATH):
        with open(COOKIE_FILE_PATH, 'r') as file:
            cookies = json.load(file)
        return cookies
    return None


def save_cookies(cookies):
    """
    Save cookies to file.
    """
    with open(COOKIE_FILE_PATH, 'w') as file:
        json.dump(cookies, file)


def youtube_downloader(link, dir_path):
    """
    Download audio from a YouTube link.
    """
    with yt_dlp.YoutubeDL({'extract_audio': True, 'format': 'bestaudio', 'outtmpl': os.path.join(dir_path, '%(id)s.wav')}) as audio:
        info_dict = audio.extract_info(link, download=True)
        id = info_dict['id']
        return os.path.join(dir_path, str(id) + ".wav")


def main():
    if 'chatbot' not in st.session_state:
        st.title("Personal assistant")
        st.subheader("Accessing personal assistant using HuggingChat")

    # Sidebar for user authentication
    st.sidebar.header("User Authentication")

    # Load cookies if available
    cookies = load_cookies()

    if cookies:
        st.session_state.cookies = cookies
        st.session_state.is_authenticated = True
        st.sidebar.success("Loaded cookies. You are connected.")
    else:
        email = st.sidebar.text_input("Email", value="", type="default")
        password = st.sidebar.text_input("Password", value="", type="password")
        if st.sidebar.button("Connect"):
            if email and password:
                # Authenticate and store cookies
                cookies = authenticate(email, password)
                st.session_state.cookies = cookies
                st.session_state.is_authenticated = True
                save_cookies(cookies)
                st.sidebar.success("Successfully connected!")
            else:
                st.error("Please provide both email and password.")

    # Check if cookies are available and user is authenticated
    if 'cookies' in st.session_state and st.session_state.is_authenticated:
        cookies = st.session_state.cookies
    else:
        st.warning("Please connect with your credentials first.")
        return

    # Pre-prompt setting
    st.sidebar.subheader('Assistants')
    st.sidebar.markdown(
        'Select an assistant to get expert help tailored to your needs. Each assistant is here to provide specialized support and guidance.')

    # Assistant type selection
    st.session_state.assistant_type = st.sidebar.selectbox(
        "Select an Assistant:",
        preprompts.keys()
    )

    st.session_state.allow_web_search = st.sidebar.checkbox(
        "Allow web search")

    # Audio download option
    if st.session_state.assistant_type == "Youtube Summary":
        youtube_link = st.sidebar.text_input("YouTube Link for Audio")
        if st.sidebar.button("Process Link", use_container_width=True):
            if youtube_link:
                with st.spinner("processing video..."):
                    audio_file = youtube_downloader(
                        youtube_link, COOKIE_PATH_DIR)
                    result = model.transcribe(audio_file)
                    result = result['text']
                    st.session_state.TTS_result = result
                    st.sidebar.success(f"Video processed")
            else:
                st.sidebar.error("Please provide a valid YouTube link.")
    else:
        st.session_state.TTS_result = ""

    ini_assistant = st.sidebar.button(
        "Initialize Assistant", type="primary", use_container_width=True)

    # Create ChatBot instance
    if ini_assistant:
        if st.session_state.assistant_type != "Youtube Summary":
            with st.spinner("Initializing Chatbot..."):
                if 'chatbot' not in st.session_state:
                    st.session_state.chatbot = hugchat.ChatBot(cookies=cookies)
                    print(st.session_state.chatbot.chat(
                        preprompts[st.session_state.assistant_type][0] + " If it is ok for you respond 'OK!'", web_search=st.session_state.allow_web_search))
        if st.session_state.assistant_type == "Youtube Summary":
            with st.spinner("Initializing Chatbot..."):
                if 'chatbot' not in st.session_state:
                    st.session_state.chatbot = hugchat.ChatBot(cookies=cookies)
                    response = st.session_state.chatbot.chat(
                        preprompts[st.session_state.assistant_type][0] + "\n" + st.session_state.TTS_result + "\n Now, return the summaries please.", web_search=st.session_state.allow_web_search)
                    preprompts[st.session_state.assistant_type][1] = response

    if 'chatbot' in st.session_state:
        st.image(preprompts[st.session_state.assistant_type][2])

        # Chat interface

        # Store LLM generated responses
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [
                {"role": "assistant", "content": preprompts[st.session_state.assistant_type][1]}]

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User-provided prompt
        if prompt := st.chat_input(disabled=not st.session_state.is_authenticated):
            st.session_state.messages.append(
                {"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

        # Generate a new response if last message is not from assistant
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                try:
                    with st.spinner("Thinking..."):
                        response = st.session_state.chatbot.chat(
                            prompt, web_search=st.session_state.allow_web_search)
                        st.markdown(response)
                except:
                    st.markdown(
                        "**ERROR**: The server is crowded, try again...")
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message)


if __name__ == "__main__":
    st.set_page_config(page_title="Personal assistant", page_icon="🤗")
    main()
