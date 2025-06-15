import streamlit as st

agentic_doc_app = st.Page("streamlit_pages/agentic_doc_app.py", title="Agentic Doc Parser")
# page_2 = st.Page("streamlit_pages/page_2.py", title="App Storage Explorer")
# page_4 = st.Page("streamlit_pages/page_4.py", title="Document Search")
pinecone_upload = st.Page("streamlit_pages/pinecone_upload.py",
                 title="Pinecone Data Upload")
pinecone_rag = st.Page("streamlit_pages/pinecone_rag.py",
                 title="Pinecone RAG")
pdf_split_merge = st.Page("streamlit_pages/pdf_split_merge.py", title="PDF Splitter")


pg = st.navigation([
    agentic_doc_app, 
    pinecone_upload,
    pinecone_rag, 
    pdf_split_merge,
                    ])

st.set_page_config(page_title="Agentic Doc Parser with Pinecone RAG",
                   page_icon=":material/edit:", layout="wide")
pg.run()
