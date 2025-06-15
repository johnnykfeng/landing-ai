import streamlit as st

page_1 = st.Page("streamlit_pages/page_1.py", title="Document Parser")
page_2 = st.Page("streamlit_pages/page_2.py", title="App Storage Explorer")
page_3 = st.Page("streamlit_pages/page_3.py", title="PDF Splitter")
page_4 = st.Page("streamlit_pages/page_4.py", title="Document Search")
page_5 = st.Page("streamlit_pages/pinecone_playground.py",
                 title="Pinecone Playground")
page_6 = st.Page("streamlit_pages/pinecone_upload.py",
                 title="PDF to Pinecone Upload")

pg = st.navigation([page_1, page_2, page_3, page_4, page_5, page_6])
st.set_page_config(page_title="Data manager",
                   page_icon=":material/edit:", layout="wide")
pg.run()
