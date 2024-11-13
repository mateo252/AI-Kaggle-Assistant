import streamlit as st


st.set_page_config(
    page_title = "AI-Kaggle-Assistant",
    page_icon = "✨",
    layout = "centered"
)

with st.sidebar:
    st.write("")        

st.markdown("""
# ✨ AI-Kaggle-Assistant

*Accelerate your data science projects with an AI-powered assistant*

---

#### Hey there, Kaggle enthusiast! 👋

This project was created as part of the implementation of the competition task on the **🔗[Kaggle](https://www.kaggle.com/competitions/gemini-long-context)** platform.
The task was to present an interesting (that's why I'm here 😎) application of Google Gemini's LLM model using its long context window, which opens up new possibilities in the world of data science.

#### 🎯 Purpose of application

The solution is designed to support data analysts in analyzing, preparing, optimizing and improving notebooks dedicated to specific competitions or datasets on the **🔗[Kaggle](https://www.kaggle.com/)** platform, **based on already existing notebooks**.
With the AI assistant, users can more easily create new notebooks, as well as improve existing projects.
AI based on ✨Gemini LLM **is more than an assistant** - it is a partner that analyzes, suggests and supports your creativity.

#### 🧩 Platform sections

Your future Kaggle notebook work center consists of two key sections:

- 💬 **About** - a current page with a greeting and summary instructions on how the site works
- ✨ **AI-Assistant** - your interactive assistant for in-depth notebook analysis. It will give you intelligent suggestions for code, optimization and document structure, fully tailored to your specific competition challenges

#### 🧭 How to begin?

Before you go to work with the service you need to prepare some important elements of the system:

- 🗝️ **Kaggle API Key** - it is needed in order to be able to extract the necessary data, which are the selected notebooks. The entire process of obtaining the key is very simple and is well described in the **🔗[Kaggle repository](https://github.com/Kaggle/kaggle-api/blob/main/docs/README.md#api-credentials)**
- 🗝️ **Gemini API Key** - the key to Gemini API is necessary in order to use selected models and functions of Google Gemini and for the proper functioning of this project. The process of obtaining the access key is possible via **🔗[AI Studio](https://aistudio.google.com/app/apikey)**. When you click on this link you will be taken to the key generation page. After accepting the terms and conditions, click **"Create API key" -> "Create API key in new project"** (if it doesn't exist yet) and it's ready.

#### 🎉 The Cool Part?
This isn't just another AI tool - it's built by a Kaggler, for Kagglers. We know the challenges, the late-night debugging sessions, and the thrill of climbing up that leaderboard. Good Luck! 😀

---

*Jump into the AI universe when you're ready to start your journey!* \\
*Remember, every great notebook starts with a single cell* 💫

*P.S. This is more than just a competition entry - it's a love letter to the Kaggle community* 💙

""")
