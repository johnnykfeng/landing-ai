import streamlit as st
from pinecone import Pinecone
import os
import pandas as pd

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
if selected_namespace is not None and st.button("Load Data as DataFrame"):
    try:
        st.info("Fetching data from Pinecone... This may take a moment.")

        all_vectors = []
        all_ids = []
        all_metadata = []

        # Use the list operation to get all vector IDs in the namespace
        for ids_batch in index.list(namespace=selected_namespace):
            if ids_batch:
                # Fetch vectors and metadata using the IDs
                vectors_data = index.fetch(
                    ids=ids_batch, namespace=selected_namespace)

                # Process each vector
                for vector_id, vector_data in vectors_data['vectors'].items():
                    all_ids.append(vector_id)
                    all_vectors.append(vector_data.get('values', []))
                    all_metadata.append(vector_data.get('metadata', {}))

        if all_ids:
            # Create DataFrame with IDs and metadata
            df = pd.DataFrame({
                'id': all_ids,
                'metadata': all_metadata
            })

            # Expand metadata columns if they exist
            if df['metadata'].apply(lambda x: bool(x)).any():
                metadata_df = pd.json_normalize(df['metadata'])
                df = pd.concat(
                    [df.drop('metadata', axis=1), metadata_df], axis=1)

            st.subheader(f"Data from {index_name}/{selected_namespace}")
            st.write(f"Total records: {len(df)}")
            st.dataframe(df)

            # Option to download as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f"{index_name}_{selected_namespace}_data.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"No vectors found in namespace '{selected_namespace}'")
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
