import streamlit as st
from pinecone import Pinecone
import os
import pandas as pd
from utils.vector_db import get_vector_db_as_df

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

st.title("Pinecone Playground")

index_name = st.text_input("Enter index name", value="paper-chunks")
index = pc.Index(index_name)

if st.button("Describe Index"):
    st.write(index.describe_index_stats())

# Get list of namespaces
namespaces = index.describe_index_stats()["namespaces"]
namespace_names = list(namespaces.keys())

selected_namespace = None
if namespace_names:
    selected_namespace = st.selectbox(
        "Select a namespace",
        namespace_names,
        key="namespace_selector"
    )
    st.write(f"Selected namespace stats:", namespaces[selected_namespace])
else:
    st.info("No namespaces found in this index")

# Button to fetch all data from the index and namespace
get_df = st.checkbox("Extract Vector DB as DataFrame", value = True)
if selected_namespace is not None and get_df:
    with st.spinner("Fetching data from Pinecone... This may take a moment."):
        df = get_vector_db_as_df(index_name=index_name, namespace=selected_namespace)
        st.caption(f"Total records: {len(df)}")
        st.caption(f"Memory usage: {df.memory_usage(deep=True).sum()/1024/1024:.2f} MB")
        with st.expander("View DataFrame"): 
            st.dataframe(df)
        
