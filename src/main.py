import streamlit as st
from config import PathVariable
import os


pg = st.navigation([
    os.path.join(PathVariable.PAGES_PATH.value, "🎉 About.py"),
    os.path.join(PathVariable.PAGES_PATH.value, "📓 Notebook-Creator.py"),
    os.path.join(PathVariable.PAGES_PATH.value, "💬 AI-Chat.py"),
    os.path.join(PathVariable.PAGES_PATH.value, "⚙️ Settings.py"),
])

pg.run()
