from dotenv import load_dotenv
import streamlit as st
import os
import kaggle
from llm import LLM
from kaggle_api import MyKaggleApi
import keyboard
import time


st.set_page_config(
    page_title = "AI-Kaggle-Assistant",
    page_icon = "✨",
    layout = "wide"
)


# Create new variable in session to check API once per start
if "API_STATUS" not in st.session_state:
    st.session_state["API_STATUS"] = {
        "GEMINI_CHECKED" : False,
        "GEMINI_WORKS" : False,
        "KAGGLE_CHECKED" : False,
        "KAGGLE_WORKS" : False
    }


if "CHAT_LLM" not in st.session_state["API_STATUS"].keys():
    st.session_state["API_STATUS"]["CHAT_LLM"] = False


# Store object of Kaggle and Gemini API
# It is used by other sites regarding this project thanks to the use of session state
if "API_OBJECTS" not in st.session_state:
    st.session_state["API_OBJECTS"] = {
        "KAGGLE_OBEJCT" : False,
        "LLM_OBJECT" : False,
    }


llm = LLM()
my_kaggle_api = MyKaggleApi()


# Display error with .env loading on sidebar
with st.sidebar:
    st.write("")
    if not load_dotenv():
        st.error(
            body=f"Error With .env",
            icon="🚨"
        )
        st.stop()

    if "MODEL_SETTINGS" in st.session_state:
        st.markdown(
            body=f"Current model:<br>**{st.session_state["MODEL_SETTINGS"]["NAME"].split("/")[1]}**",
            unsafe_allow_html=True
        )


# If the '.kaggle' file is found and the API is working
if not st.session_state["API_STATUS"]["KAGGLE_CHECKED"]:
    api = kaggle.KaggleApi()
    api.authenticate()
    
    try:
        api.kernels_list(page=1, page_size=1)
        
    except Exception as e:
        st.session_state["API_STATUS"]["KAGGLE_CHECKED"] = True
        st.session_state["API_STATUS"]["KAGGLE_WORKS"] = False

    else:
        st.session_state["API_STATUS"]["KAGGLE_CHECKED"] = True
        st.session_state["API_STATUS"]["KAGGLE_WORKS"] = True
        
        

# Create object of Kaggle API every refresh
if st.session_state["API_STATUS"]["KAGGLE_CHECKED"] and st.session_state["API_STATUS"]["KAGGLE_WORKS"]:
    api = kaggle.KaggleApi()
    api.authenticate()
    
    st.session_state["API_OBJECTS"]["KAGGLE_OBJECT"] = my_kaggle_api
    my_kaggle_api.load_api(api)


# If the Gemini API works
if not st.session_state["API_STATUS"]["GEMINI_CHECKED"]:

    try:
        llm.connect_client(os.environ.get("GEMINI_API", ""))
        llm.get_models_list()
                
    except Exception as e:
        st.session_state["API_STATUS"]["GEMINI_CHECKED"] = True
        st.session_state["API_STATUS"]["GEMINI_WORKS"] = False
                    
    else:
        st.session_state["API_STATUS"]["GEMINI_CHECKED"] = True
        st.session_state["API_STATUS"]["GEMINI_WORKS"] = True


# Loading setting of Gemini API
if st.session_state["API_STATUS"]["GEMINI_CHECKED"] and st.session_state["API_STATUS"]["GEMINI_WORKS"] and load_dotenv():
    st.session_state["API_OBJECTS"]["LLM_OBJECT"] = llm
    llm.connect_client(os.environ.get("GEMINI_API", ""))
    

# Call error with Kaggle API
if st.session_state["API_STATUS"]["KAGGLE_CHECKED"] and not st.session_state["API_STATUS"]["KAGGLE_WORKS"]:
    st.error(
        body=f"Error With Kaggle API",
        icon="🚨"
    )
    st.stop()
    

# Call error with Gemini API
if st.session_state["API_STATUS"]["GEMINI_CHECKED"] and not st.session_state["API_STATUS"]["GEMINI_WORKS"]:
    st.error(
        body=f"Error With Gemini API Key",
        icon="🚨"
    )
    st.stop()


####### MAIN SECTION OF SETTINGS TO CHOOSE MODEL #######

st.markdown("""
# ⚙️ Settings         
---
""")

with st.columns(2)[0]:
    
    has_mode_settings = "MODEL_SETTINGS" in st.session_state
    temp = st.session_state["MODEL_SETTINGS"]["TEMPERATURE"] if has_mode_settings else 0.2
    top_k = st.session_state["MODEL_SETTINGS"]["TOP_P"] if has_mode_settings else 0.80
    top_p = st.session_state["MODEL_SETTINGS"]["TOP_K"] if has_mode_settings else 32

    available_llm_models = llm.get_models_list()
    selected_model = st.selectbox(
        label="Gemini Models",
        options=available_llm_models,
        placeholder="Select a model",
        index=available_llm_models.index("models/gemini-2.5-flash-preview-05-20")
    )
    selected_temperature = st.number_input(
        label="Temperature",
        min_value=0.0,
        max_value=2.0,
        step=0.01,
        value=temp
    )
    selected_top_p = st.number_input(
        label="Top P",
        min_value=0.0,
        max_value=1.0,
        step=0.01, value=top_k
    )
    selected_top_k = st.number_input(
        label="Top K",
        min_value=0,
        max_value=1000,
        step=1,
        value=top_p
    )


    if st.button(
        label="Save",
        icon="📝"
    ):
        parameters_llm_model = llm.get_model_parameters(selected_model)
        st.session_state["MODEL_SETTINGS"] = {
            "NAME" :              selected_model,
            "TEMPERATURE" :       selected_temperature,
            "TOP_P" :             selected_top_p,
            "TOP_K" :             selected_top_k,
            "MAX_INPUT_TOKENS" :  parameters_llm_model["max_input_tokens"],  # type: ignore
            "MAX_OUTPUT_TOKENS" : parameters_llm_model["max_output_tokens"]  # type: ignore
        }
        
        st.success(
            body="Saved",
            icon="✔️"
        )

        time.sleep(.1)
        keyboard.press_and_release("enter")