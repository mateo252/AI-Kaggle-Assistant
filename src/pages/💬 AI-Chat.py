import os
import streamlit as st
from data_maker import DataMaker


st.set_page_config(
    page_title = "AI-Kaggle-Assistant",
    page_icon = "✨",
    layout = "wide"
)


with st.sidebar:
    st.write("")
    if "MODEL_SETTINGS" not in st.session_state or "API_OBJECTS" not in st.session_state: 
        st.error(
            body=f"Choose model in settings",
            icon="🚨"
        )
    else:
        st.markdown(
            body=f"Current model:<br>**{st.session_state["MODEL_SETTINGS"]["NAME"].split("/")[1]}**",
            unsafe_allow_html=True
        )


if "MODEL_SETTINGS" in st.session_state and "API_OBJECTS" in st.session_state:

    # This 'if' protects against recreating the chat session
    if st.session_state["API_STATUS"]["CHAT_LLM"] is False:
        st.session_state["API_OBJECTS"]["LLM_OBJECT"].create_chat(st.session_state["MODEL_SETTINGS"]["NAME"])
        st.session_state["API_STATUS"]["CHAT_LLM"] = True

    maker = DataMaker()

    st.markdown("""
    # 💬 AI-Chat
    ---
    """)

    with st.sidebar:
        if st.button(label="Clear chat", icon="🧹"):
            st.session_state["messages"] = [{"role"   : "assistant", 
                                            "content" : "Hey!<br>How can I help you?<br>You can ask and attach a Markdown or Notebook file",
                                            "avatar"  : "🧠"}]
            st.session_state["API_OBJECTS"]["LLM_OBJECT"].create_chat(st.session_state["MODEL_SETTINGS"]["NAME"])


    # Make messages history for AI
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role"   : "assistant", 
                                        "content" : "Hey!<br>How can I help you?<br>You can ask and attach a Markdown or Notebook file",
                                        "avatar"  : "🧠"}]

    # Display initial message from AI
    for msg in st.session_state["messages"]:
        st.chat_message(
            name=msg["role"],
            avatar=msg["avatar"]
        ).write(msg["content"], unsafe_allow_html=True)
        

    # Get user input
    if user_prompt := st.chat_input(
        placeholder="Your question...(max 512 chars)", 
        max_chars=512, 
        accept_file=True, 
        file_type=["ipynb", "md"]
    ):
        
        if user_prompt["files"]:
            user_message_display = f"📎File: **{user_prompt["files"][0].name}**<br>{user_prompt["text"]}" # type: ignore
            if os.path.splitext(user_prompt["files"][0].name)[1] == ".ipnyb": # type: ignore
                loaded_md_file = maker.convert_ipynb_to_markdown(user_prompt["files"][0].getvalue().decode("utf-8")) # type: ignore

            else:
                loaded_md_file = user_prompt["files"][0].getvalue().decode("utf-8") # type: ignore

            user_message_llm = f"{user_prompt["text"]}<br><br>File as Markdown:<br>{loaded_md_file}"

        else:
            user_message_display = user_prompt["text"]
            user_message_llm = user_message_display


        st.chat_message("user", avatar="😎").write(
            user_message_display,
            unsafe_allow_html=True
        )
        st.session_state["messages"].append({"role"  : "user", 
                                            "content": user_message_display,
                                            "avatar" : "😎"})
        
        llm_response = st.session_state["API_OBJECTS"]["LLM_OBJECT"].send_message(user_message_llm)
        with st.chat_message("assistant", avatar="🧠"):
            ai_response = st.write(
                llm_response, 
                unsafe_allow_html=True
            )

        st.session_state["messages"].append({"role"  : "assistant", 
                                            "content": llm_response,
                                            "avatar" : "🧠"})
        

        # TO-DO
        # Save chat history