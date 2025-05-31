import streamlit as st


st.set_page_config(
    page_title = "AI-Kaggle-Assistant",
    page_icon = "✨",
    layout = "centered"
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


st.markdown("""
# ✨ AI-Kaggle-Assistant

*Accelerate your data science projects with an AI-powered assistant*

---

#### Hey there, Kaggle enthusiast! 👋

This project was created as part of the implementation of the competition task on the **🔗[Kaggle](https://www.kaggle.com/competitions/gemini-long-context)** platform.
The assignment was to demonstrate the use of Google Gemini's LLM model using its long context window, which opens up new possibilities in the world of data science.

#### 🎯 Purpose of application

The solution is designed to support data analysts in analyzing, preparing, optimizing and improving notebooks dedicated to specific competitions or datasets on the **🔗[Kaggle](https://www.kaggle.com/)** platform.
With the AI assistant, users can more easily create new notebooks, as well as improve existing projects.

#### 🧩 Platform sections

Your future Kaggle notebook work center consists of few several sections:

- 🎉 **About** - a current page with a greeting and summary instructions on how the site works
- 📓 **Notebook Creator** - a page where you can generate a whole notebook based on a selected dataset
- 💬 **AI Chat** - the place where you can talk to Gemini about your chosen notebook project
- ⚙️ **Settings** - before you start work, choose the model and parameters
                        
#### 🧭 How to begin?

Before you go to work with the service you need to prepare some important elements of the system:

- 🗝️ **Kaggle API Key** - it is needed in order to be able to extract the necessary data, which are the selected notebooks. The entire process of obtaining the key is very simple and is well described in the **🔗[Kaggle repository](https://github.com/Kaggle/kaggle-api/blob/main/docs/README.md#api-credentials)**
- 🗝️ **Gemini API Key** - the key to Gemini API is necessary in order to use selected models and functions of Google Gemini and for the proper functioning of this project. The process of obtaining the access key is possible via **🔗[AI Studio](https://aistudio.google.com/app/apikey)**. When you click on this link you will be taken to the key generation page. After accepting the terms and conditions, click **"Create API key" -> "Create API key in new project"** (if it doesn't exist yet) and it's ready.

---

*Jump into the AI universe when you're ready to start your journey!* \\
*Remember, every great notebook starts with a single cell* 💫

""")
