from data_maker import DataMaker
from config import PathVariable
import streamlit as st
import os


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


start_main_section = "MODEL_SETTINGS" in st.session_state and "API_OBJECTS" in st.session_state
if start_main_section:

    st.session_state["API_OBJECTS"]["LLM_OBJECT"].connect_client(os.environ.get("GEMINI_API", ""))

    maker = DataMaker()
    maker.prepare_data_dir()

    selected_model =       st.session_state["MODEL_SETTINGS"]["NAME"]
    selected_temperature = st.session_state["MODEL_SETTINGS"]["TEMPERATURE"]
    selected_top_p =       st.session_state["MODEL_SETTINGS"]["TOP_P"]
    selected_top_k =       st.session_state["MODEL_SETTINGS"]["TOP_K"]
    max_input_tokens =     st.session_state["MODEL_SETTINGS"]["MAX_INPUT_TOKENS"]
    max_output_tokens =    st.session_state["MODEL_SETTINGS"]["MAX_OUTPUT_TOKENS"]

    # Header for the page
    st.markdown("""
    # 📓 Notebook-Creator

    *Unlock new levels of productivity in data science using AI-driven support*
                
    ---
    """)
    
    # First row is for mode selction and dataset or competition 
    inputs_columns_first_row = st.columns(
        spec=3,
        vertical_alignment="bottom"
    )
    
    ## Make column for mode selection for generator
    with inputs_columns_first_row[0]:
        selected_mode = st.selectbox(
            label="Mode",
            options=["Generate the notebook"],
            placeholder="Select a mode"
        )
       
    ## Make subcolumns for input surce
    with inputs_columns_first_row[1]:
        source_columns = st.columns(2)
        selected_dataset = source_columns[0].text_input(
            label="Dataset",
            placeholder="[owner]/[dataset-name]"
        )
        selected_competition = source_columns[1].text_input(
            label="Competition",
            placeholder="e.g. titanic"
        )
        
    # Start button in last main column and first of three subcolumns
    start_button = inputs_columns_first_row[2].columns(3)[0].button(
        label="Start",
        use_container_width=True,
        icon="🚀"
    )
    
    # Next, second row
    inputs_columns_second_row = st.columns(
        spec=3,
        vertical_alignment="top"
    )
    with inputs_columns_second_row[0]:
        page_columns = st.columns(
            spec=3,
            vertical_alignment="top"
        )
        selected_page_num  = page_columns[0].number_input(
            label="Pages",
            min_value=1,
            max_value=10,
            step=1,
            value=1
        )
        selected_page_size = page_columns[1].number_input(
            label="Page Size",
            min_value=1,
            max_value=100,
            step=1,
            value=20
        )
        selected_page_sort = page_columns[2].selectbox(
            label="Sort By",
            options=["voteCount", "viewCount", "hotness", "commentCount", "dateCreated", "dateRun", "relevance"]
        )

        selected_generated_notebook = st.selectbox(
            label="Ready Notebooks",
            options=maker.get_notebooks_list(),
            placeholder="Select a notebook"
        )
        display_generated_notebook = st.button(
            label="Show",
            use_container_width=True,
            icon="🔎"
        )
            
    st.markdown("---")
    
    if start_main_section and start_button:
        if (selected_dataset and selected_competition) or (selected_dataset == "" and selected_competition == ""):
            with st.columns(3)[1]:
                st.error(
                    body="Only Dataset Or Competition",
                    icon="🚨"
                )
                st.stop()
        
        with st.spinner("Processing data..."):
            # Config for getting kernels (notebooks) list       
            my_kaggle_api_config = {
                "page"      : selected_page_num,
                "page_size" : selected_page_size,
                "language"  : "python",
                "sort_by"   : str(selected_page_sort)
            }
        
            # Config for LLM model
            model_params = {
                "temperature" : selected_temperature,
                "top_p" : selected_top_p,
                "top_k" : selected_top_k,
                "max_output_tokens" : max_output_tokens
            }
                
            if selected_dataset:
                kernels_list = st.session_state["API_OBJECTS"]["KAGGLE_OBJECT"].get_kernels_list(
                    dataset=selected_dataset,
                    **my_kaggle_api_config
                )
                if len(kernels_list) == 0:
                    with st.columns(3)[1]:
                        st.error(
                            body="No Dataset Notebooks Detected",
                            icon="🚨"
                        )
                        st.stop()
                            
                kernels_metadata = st.session_state["API_OBJECTS"]["KAGGLE_OBJECT"].get_kernels_specification(kernels_list)
                    
            else:
                kernels_list = st.session_state["API_OBJECTS"]["KAGGLE_OBJECT"].get_kernels_list(
                    competition=selected_competition,
                    **my_kaggle_api_config
                )
                if len(kernels_list) == 0:
                    with st.columns(3)[1]:
                        st.error(
                            body="No Competition Notebooks Detected",
                            icon="🚨"
                        )
                        st.stop()
                            
                kernels_metadata = st.session_state["API_OBJECTS"]["KAGGLE_OBJECT"].get_kernels_specification(kernels_list)
             
            # Save 'source' in JSON to .ipynb file
            for metadata in kernels_metadata:
                if not maker.download_notebook(metadata):
                    with st.columns(3)[1]:
                        st.error(
                            body="Error With Saving Notebook",
                            icon="🚨"
                        )
                        st.stop()
                            
            # Load file base on mode - generate new or upgrade own notebook
            file_mode = "generate_notebook_prompt.txt"
            
            # Ready to use prompt
            if isinstance(prompt := maker.make_notebook_generator_prompt(
                kernels_spec=kernels_metadata, 
                file_instruction=file_mode
            ), bool):
                st.error(
                    body="Error With Making Prompt",
                    icon="🚨"
                )
                st.stop()

            # Limit prompt to model limit tokens
            if st.session_state["API_OBJECTS"]["LLM_OBJECT"].count_tokens(selected_model, prompt) > max_input_tokens:
                st.error(
                    body="To Many Input Tokens. Chnage 'Pages' or 'Page Size'",
                    icon="🚨"
                )
                st.stop()

            # Loop for generating output if LLM return invalid JSON format
            while True:
                if not isinstance(response := st.session_state["API_OBJECTS"]["LLM_OBJECT"].generate_notebook(
                    selected_model,
                    prompt,
                    **model_params
                ), bool):
                    break
                
       
        # Main container contains information
        with st.container(border=True):
            st.markdown("#### 📑 Generated Notebook")
            
            save_columns = st.columns(4)
            right_tabs_text , right_tabs_json= st.tabs(["📝 Text", "💻 JSON"])
            
            # SECTION FOR MAKING TEMPLATE FOR GENERATED DATA #
            try:
                # Read template for analyzed notebooks
                with open(
                    file=os.path.join(PathVariable.TEMPLATE_PATH.value, "generated_notebook_template.txt"), 
                    mode="r", 
                    encoding="utf-8"
                ) as f:
                    generated_template = f.read()
                    
            except Exception as e:
                with st.columns(3)[1]:
                    st.error(
                        body="Error Reading Template - generated_notebook_template.txt",
                        icon="🚨"
                    )
                    st.stop()

            # Tab with text
            with right_tabs_text:
                md_generated_notebook = maker.format_generated_notebook(
                    generated_notebook_data=response.get("new_notebook"), 
                    template=generated_template
                )
                st.markdown(md_generated_notebook)

            # Tab with JSON
            with right_tabs_json:
                st.json(
                    body=response.get("new_notebook"),
                    expanded=False
                )
                
            # Save notebook to 'Save'
            name = selected_dataset if selected_dataset else selected_competition
            if maker.save_new_markdown(
                markdown_text=md_generated_notebook, 
                name=name
            ):
                save_columns[0].info(
                    body="Saved",
                    icon="✔️"
                )

            else:
                save_columns[0].error(
                    body="Saving Error",
                    icon="🚨"
                )
                st.stop()

    # Show ready notebooks
    elif start_main_section and display_generated_notebook:
        with open(
            file=os.path.join(PathVariable.SAVE_PATH.value, selected_generated_notebook),
            mode="r",
            encoding="utf-8"
        ) as f:
            open_notebook = f.read()

        with st.tabs(["📝 Text", " "])[0]:
            with st.container(border=True):
                st.markdown(open_notebook)
        
