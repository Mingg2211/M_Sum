import streamlit as st
from src.summarization import M_Sum
import os

@st.cache_resource
def load_model():
    sum = M_Sum()
    return sum
sum = load_model()
#streamlit
st.title("AIA M_Summarizer")
st.subheader("Paste any article in text area below and click on the 'Summarize Text' button to get the summarized textual data.")
st.subheader("Or enter a url from news stites such as dantri.com and click on the 'Import Url' button to get the summarized.")
st.subheader('This application is powered by Minggz.')
st.write('Paste your copied data or news url here ...')
txt = st.text_area(label='Input', placeholder='Try me', max_chars=5000, height=50)
print(txt)
col1, col2 = st.columns([2,6],gap='large')
with col1:
    summarize_button = st.button(label='Summarize Text')
with col2:
    import_button = st.button(label='Import Url')

if summarize_button :
    result = sum.summary_doc(txt)
    st.write(result)
    print('------------1--------------')
if import_button:
    result = sum.summary_url(dantri_url=txt)
    st.write(txt)
    st.write(result)
    print('------------1--------------')