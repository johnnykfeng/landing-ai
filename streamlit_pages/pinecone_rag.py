import os
import json
import numpy as np
import pandas as pd
import streamlit as st
from pinecone import Pinecone
from pathlib import Path
from utils.vector_db import get_vector_db_as_df
from utils.visualization import (viz_chunk_in_pdf, 
                                 draw_box_on_page, 
                                 pdf_to_images)
from utils.vector_db import (query_to_embedding, 
                             rag_response, 
                             retrieval_augmented_prompt,
                             retrieve_contexts)

@st.cache_data
def get_vector_db_as_df_cached(index_name: str, namespace: str) -> pd.DataFrame:
    return get_vector_db_as_df(index_name, namespace)

@st.cache_data
def viz_chunk_in_pdf_cached(index_name: str, 
                            chunk_id: str, 
                            namespace: str, 
                            pdf_filepath: str,
                            color: tuple[int, int, int] = (0, 255, 0), 
                            thickness: int = 2) -> np.ndarray:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)
    fetched_results = index.fetch(ids=[chunk_id], namespace=namespace)
    box_json = fetched_results.vectors[chunk_id].metadata['box']
    box_json = json.loads(box_json)
    page_number = fetched_results.vectors[chunk_id].metadata['pdf_page']
    page_number = int(page_number)  
    images = pdf_to_images(pdf_filepath)
    img = images[page_number]
    img = draw_box_on_page(box_json, img, color, thickness)
    return img

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

st.title("RAG with Pinecone")
col1, col2 = st.columns(2)
with col1:
    index_name = st.text_input("Enter index name", value="paper-chunks")
    index = pc.Index(index_name)

    if st.button("Describe Index"):
        st.write(index.describe_index_stats())

with col2:
    # Get list of namespaces
    namespaces = index.describe_index_stats()["namespaces"]
    namespace_names = list(namespaces.keys())

    selected_namespace = None
    if namespace_names:
        selected_namespace = st.selectbox(
            "Select a namespace",
            namespace_names,
            key="namespace_selector",
        )
        # st.write(f"Selected namespace stats:", namespaces[selected_namespace])
    else:
        st.info("No namespaces found in this index")

# Button to fetch all data from the index and namespace
# get_df = st.checkbox("Extract Vector DB as DataFrame", value = True)
if selected_namespace is not None:
    df = get_vector_db_as_df_cached(index_name=index_name, namespace=selected_namespace)
    with col2:
        st.caption(f"Total records: {len(df)}")
        st.caption(f"Memory usage: {df.memory_usage(deep=True).sum()/1024/1024:.2f} MB")
    with st.expander(f"Dataframe for Vector DB: {selected_namespace}"): 
        st.dataframe(df)
        
if namespace_names:
    col1, col2 = st.columns(2)
    with col1:
        chunk_id = st.selectbox("Select a chunk id", df['id'])
    with col2:
        fetched_results = index.fetch(ids=[chunk_id], namespace=selected_namespace)
        with st.expander("View Metadata"):  
            st.write(fetched_results.vectors[chunk_id].metadata)
    
if st.button("Visualize chunk in PDF"):
    pdf_folder = Path(r"C:\Users\johnk\Projects-code\LEARN\landing-ai\app_storage\original_files")
    pdf_filepath = pdf_folder / f"{selected_namespace}.pdf"
    
    viz = viz_chunk_in_pdf_cached(
        index_name=index_name, 
        chunk_id=chunk_id, 
        namespace=selected_namespace, 
        pdf_filepath=pdf_filepath,
        color=(0, 255, 0), 
        thickness=2)
    st.image(viz)

st.divider()
########################################################
## Retrieval Augmented Generation #######################
########################################################
st.subheader("Retrieval Augmented Generation")

col1, col2 = st.columns(2)
with col1:
    query_text = st.text_input("Enter a query")
with col2:
    top_k = st.number_input("Enter top k", value=3, min_value=1, max_value=10)

retrieve_chunks = st.toggle("Retrieve Chunks", value=False)

if retrieve_chunks:
    if query_text:
        chunk_ids, metadata_list = retrieve_contexts(
            query_text, index_name, selected_namespace, top_k)
        
    retrieved_df = pd.DataFrame(metadata_list, index=chunk_ids)
    with st.expander("Retrieved Chunks"):
        st.dataframe(retrieved_df)
    context_list = [metadata_list[i]['chunk_text'] for i in range(len(chunk_ids))]
    pdf_folder = Path(r"C:\Users\johnk\Projects-code\LEARN\landing-ai\app_storage\original_files")
    pdf_filepath = pdf_folder / f"{selected_namespace}.pdf"
    for chunk_id in chunk_ids:
        with st.expander(f"Visualize {chunk_id}"):
            st.image(viz_chunk_in_pdf_cached(
                                index_name=index_name, 
                                chunk_id=chunk_id, 
                                namespace=selected_namespace, 
                                pdf_filepath=pdf_filepath,
                                color=(0, 255, 0), 
                                thickness=2))
            
        
    if st.button("RAG Response", key="rag_response"):
        try:
            rag_response_text = rag_response(context_list, query_text)
            st.markdown(rag_response_text)
        except Exception as e:
            st.error(f"Error: {e}")
            
        

    
