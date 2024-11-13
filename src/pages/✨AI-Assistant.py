import streamlit as st
import google.generativeai as genai
import kaggle
from variables import PathVariable as path_vars
from kaggle_api import MyKaggleApi
from data_maker import DataMaker
from llm_api import ApiLLM
from dotenv import load_dotenv
import os
import pandas as pd


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
        "KAGGLE_WORKS" : False,
    }

my_kaggle_api = MyKaggleApi()
maker = DataMaker()
llm = ApiLLM()

# Display error with .env loading on sidebar
with st.sidebar:
    st.write("")
    if not load_dotenv():
        st.error(f"Error With .env", icon="🚨")
        st.stop()


# If the .kaggle file is found and the API is working
if not st.session_state["API_STATUS"]["KAGGLE_CHECKED"]:
    api = kaggle.KaggleApi(kaggle.ApiClient())
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
    api = kaggle.KaggleApi(kaggle.ApiClient())
    api.authenticate()
    
    my_kaggle_api.load_api(api)
    maker.load_api(api)


# If the Gemini API works
if not st.session_state["API_STATUS"]["GEMINI_CHECKED"]:

    try:
        genai.configure(api_key=os.environ.get("GEMINI_API"))
        llm.get_models_list()
                
    except Exception as e:
        st.session_state["API_STATUS"]["GEMINI_CHECKED"] = True
        st.session_state["API_STATUS"]["GEMINI_WORKS"] = False
                    
    else:
        st.session_state["API_STATUS"]["GEMINI_CHECKED"] = True
        st.session_state["API_STATUS"]["GEMINI_WORKS"] = True


# Loading setting of Gemini API
if st.session_state["API_STATUS"]["GEMINI_CHECKED"] and st.session_state["API_STATUS"]["GEMINI_WORKS"] and load_dotenv():
    genai.configure(api_key=os.environ.get("GEMINI_API"))
    

with st.sidebar:
    # Call error with Kaggle API
    if st.session_state["API_STATUS"]["KAGGLE_CHECKED"] and not st.session_state["API_STATUS"]["KAGGLE_WORKS"]:
        st.error(f"Error With Kaggle API", icon="🚨")
        st.stop()
    
    # Call error with Gemini API
    if st.session_state["API_STATUS"]["GEMINI_CHECKED"] and not st.session_state["API_STATUS"]["GEMINI_WORKS"]:
        st.error(f"Error With Gemini API Key", icon="🚨")
        st.stop()

    selected_model = st.selectbox("Gemini Models", options=["gemini-1.5-flash", "gemini-1.5-pro"], placeholder="Select a model")
    selected_temperature = st.number_input("Temperature", min_value=0.0, max_value=2.0, step=0.01, value=0.2)
    selected_top_p = st.number_input("Top P", min_value=0.0, max_value=1.0, step=0.01, value=0.80)
    selected_top_k = st.number_input("Top K", min_value=0, max_value=1000, step=1, value=32)
    
    start_main_section = True
    
uploaded_notebook = None
if start_main_section:
    # Header for the page
    st.markdown("""
    # ✨ AI-Kaggle-Assistant

    *Unlock new levels of productivity in data science using AI-driven support*

    ---
    """)
    
    # First row is for mode selction and dataset or competition 
    inputs_columns_first_row = st.columns(3, vertical_alignment="bottom")
    
    # Make column for mode selection for generator
    with inputs_columns_first_row[0]:
        selected_mode = st.selectbox("Mode", options=["Generate the notebook", "Improve the notebook"], placeholder="Select a mode")
       
    # Make subcolumns for input surce
    with inputs_columns_first_row[1]:
        source_columns = st.columns(2)
        selected_dataset = source_columns[0].text_input("Dataset", placeholder="[owner]/[dataset-name]")
        selected_competition = source_columns[1].text_input("Competition", placeholder="e.g. titanic")
        
    # Start button in last main column and first of three subcolumns    
    start_button = inputs_columns_first_row[2].columns(3)[0].button("Start", use_container_width=True, icon="🚀")
    
    # Next, second row
    inputs_columns_second_row = st.columns(3, vertical_alignment="top")
    with inputs_columns_second_row[0]:
        if selected_mode == "Generate the notebook":
            page_columns = st.columns(3, vertical_alignment="top")
            selected_page_num  = page_columns[0].number_input("Pages", min_value=1, max_value=10, step=1, value=1)
            selected_page_size = page_columns[1].number_input("Page Size", min_value=1, max_value=100, step=1, value=20)
            selected_page_sort = page_columns[2].selectbox("Sort By", options=["voteCount", "viewCount", "hotness", "commentCount", "dateCreated", "dateRun", "relevance"])

        else:    
            uploaded_notebook = st.file_uploader("Upload", type=["ipynb"])
            
    with inputs_columns_second_row[1]:
        if not selected_mode == "Generate the notebook":
            page_columns = st.columns(3, vertical_alignment="top")
            selected_page_num  = page_columns[0].number_input("Pages", min_value=1, max_value=10, step=1, value=1)
            selected_page_size = page_columns[1].number_input("Page Size", min_value=1, max_value=100, step=1, value=20)
            selected_page_sort = page_columns[2].selectbox("Sort By", options=["voteCount", "viewCount", "hotness", "commentCount", "dateCreated", "dateRun", "relevance"])

    st.markdown("---")
    
    
    if start_main_section and start_button:
        if (selected_dataset and selected_competition) or (selected_dataset == "" and selected_competition == ""):
            with st.columns(3)[1]:
                st.error("Only Dataset Or Competition", icon="🚨")
                st.stop()
        
        with st.spinner("Processing data..."):
            # Load selected model
            llm.load_model(selected_model)
             
            # Clear dirs with previous files
            maker.preparations_data_dirs()
                
            # Config for getting kernels (notebooks) list       
            my_kaggle_api_config = {
                "page_num"  : str(selected_page_num),  # type: ignore
                "page_size" : str(selected_page_size), # type: ignore
                "language"  : "python",
                "sort_by"   : str(selected_page_sort)  # type: ignore
            }
        
            # Config for LLM model
            model_params = {
                "temperature" : selected_temperature,
                "top_p" : selected_top_p,
                "top_k" : selected_top_k
            }
                
            if selected_dataset:
                kernels_list = my_kaggle_api.get_kernels_list(dataset=selected_dataset, **my_kaggle_api_config)
                if len(kernels_list) == 0:
                    with st.columns(3)[1]:
                        st.error("No Notebooks Detected", icon="🚨")
                        st.stop()
                            
                kernels_metadata = my_kaggle_api.get_kernels_specification(kernels_list)
                    
            else:
                kernels_list = my_kaggle_api.get_kernels_list(competition=selected_competition, **my_kaggle_api_config)
                if len(kernels_list) == 0:
                    with st.columns(3)[1]:
                        st.error("No Notebooks Detected", icon="🚨")
                        st.stop()
                            
                kernels_metadata = my_kaggle_api.get_kernels_specification(kernels_list)
             
            # Save 'source' in JSON to .ipynb file
            for val in kernels_metadata:
                if not maker.download_notebook(val):
                    with st.columns(3)[1]:
                        st.error("Error With Saving Notebook", icon="🚨")
                        st.stop()
                            
            # Load file base on mode - generate new or upgrade own notebook
            file_mode = "generate_notebook_prompt.txt" if selected_mode == "Generate the notebook" else "improve_notebook_prompt.txt"
            
            # Ready to use prompt
            if selected_mode == "Generate the notebook":
                if isinstance(prompt := maker.make_notebook_prompt(kernels_metadata, file_mode), bool):
                    st.error("Error With Making Prompt", icon="🚨")
                    st.stop()
                    
            else:
                # If mode set to improve my notebook
                if uploaded_notebook is not None:
                    if isinstance(prompt := maker.make_notebook_prompt(kernels_metadata, file_mode, uploaded_notebook), bool):
                        st.error("Error With Making Prompt", icon="🚨")
                        st.stop()
                else:
                    st.error("Problem With File Uploader", icon="🚨")
                    st.stop()
                    
            # Limit prompt to 1 00 000 tokens
            if llm.get_count_tokens(prompt) > 1_000_000:
                st.error("To Many Input Tokens. Chnage 'Pages' or 'Page Size'", icon="🚨")
                st.stop()

            # Loop for generating output if LLM return invalid JSON format
            while True:
                if selected_mode == "Generate the notebook":
                    if not isinstance(model_outputs := llm.generate_output(prompt, **model_params), bool):
                        break
                else:
                    if not isinstance(model_outputs := llm.generate_output(prompt, True, **model_params), bool):
                        break
        
        response, response_stats = model_outputs
        medals = {
            1 : "🥇",
            2 : "🥈",
            3 : "🥉",
        }   
    
        results_columns = st.columns(2)
        
        # Left column contains information on the 3 analyzed notebooks 
        with results_columns[0]:
            with st.container(border=True):
                st.markdown(f"#### 📊 Top {len(response.get("notebook_analyses", None)[:3])} Notebooks")
                left_tabs_text , left_tabs_json= st.tabs(["📝 Text", "💻 JSON"])
                
                with left_tabs_text:
                    try:
                        # Read template for analyzed notebooks
                        with open(os.path.join(path_vars.TEMPLATE_PATH.value, "kaggle_notebook_template.txt"), "r", encoding="utf-8") as f:
                            kaggle_template = f.read()
                            
                    except Exception as e:
                        with st.columns(3)[1]:
                            st.error("Error Reading Template - kaggle_notebook_template.txt", icon="🚨")
                            st.stop()
                        
                    for enum, val in enumerate(response.get("notebook_analyses")):
                        with st.expander(f"**{val.get('author')}**", icon=medals.get(enum+1)):
                            st.markdown(maker.format_kaggle_notebook(val, kaggle_template), unsafe_allow_html=True)
                            
                with left_tabs_json:
                    st.json(response.get("notebook_analyses"), expanded=False)
                   
                    
        # Right column contains information with data for new notebook or elements to improve
        with results_columns[1]:
            with st.container(border=True):
                if selected_mode == "Generate the notebook":
                    st.markdown("#### 📑 Generated Notebook")
                
                else:
                    st.markdown("#### 🚀 Improved Notebook")
                    
                save_columns = st.columns(4)
                right_tabs_text , right_tabs_json= st.tabs(["📝 Text", "💻 JSON"])
                
                # SECTION FOR MAKING TEMPLATE FOR GENERATED DATA
                if selected_mode == "Generate the notebook":
                    try:
                        # Read template for analyzed notebooks
                        with open(os.path.join(path_vars.TEMPLATE_PATH.value, "generated_notebook_template.txt"), "r", encoding="utf-8") as f:
                            generated_template = f.read()
                            
                    except Exception as e:
                        with st.columns(3)[1]:
                            st.error("Error Reading Template - generated_notebook_template.txt", icon="🚨")
                            st.stop()

                    # Tab with text
                    with right_tabs_text:
                        md_generated_notebook = maker.format_generated_notebook(response.get("new_notebook"), generated_template)
                        st.markdown(md_generated_notebook)

                    # Tab with JSON
                    with right_tabs_json:
                        st.json(response.get("new_notebook"), expanded=False)
                        
                    # Save notebook to 'Save'    
                    if maker.save_new_markdown(md_generated_notebook):  # type: ignore
                        save_columns[0].info("Saved", icon="✔️")

                    else:
                        save_columns[0].error("Saving Error", icon="🚨")
                        st.stop()
                                           
                else:
                    if uploaded_notebook is not None:
                        try:
                            # Read template for analyzed notebooks
                            with open(os.path.join(path_vars.TEMPLATE_PATH.value, "improved_notebook_template.txt"), "r", encoding="utf-8") as f:
                                generated_template = f.read()
                                
                        except Exception as e:
                            with st.columns(3)[1]:
                                st.error("Error Reading Template - improved_notebook_template.txt", icon="🚨")
                                st.stop()

                        # Tab with text
                        with right_tabs_text:
                            md_improved_notebook = maker.format_improved_notebook(response.get("improved_notebook"), generated_template)
                            st.markdown(md_improved_notebook, unsafe_allow_html=True)

                        # Tab with JSON
                        with right_tabs_json:
                            st.json(response.get("improved_notebook"), expanded=False)

                        # Save notebook to 'Save'
                        if maker.save_new_markdown(md_improved_notebook, True):  # type: ignore
                            save_columns[0].info("Saved", icon="✔️")
                        
                        else:
                            save_columns[0].error("Saving Error", icon="🚨")
                            st.stop()
                
        with st.sidebar:
            st.markdown("---")
            response_stats_df = pd.DataFrame(response_stats, index=["Results"]) 
            response_stats_df.rename(columns={"model_prompt_token_count"     : "Prompt Tokens",
                                              "model_candidates_token_count" : "Response Tokens",
                                              "model_total_token_count"      : "Total Tokens",
                                              "response_time"                : "Response Time"}, inplace=True)
            st.table(response_stats_df.T)