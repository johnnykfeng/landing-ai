import os
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st
import pandas as pd
from pinecone import Pinecone
from agentic_doc.parse import parse
from utils.serialization import (extract_json_from_parsed_doc,
                                 parsed_doc_to_records)

# Initialize Pinecone client


@st.cache_resource
def get_pinecone_client():
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        st.error("PINECONE_API_KEY not found in environment variables")
        st.stop()
    return Pinecone(api_key=api_key)


pc = get_pinecone_client()

st.title("📄 PDF to Pinecone Upload Pipeline")
st.markdown("Upload PDFs, parse them with agentic_doc, and upload to Pinecone vector database with full manual control.")

# Initialize session state
if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = None
if 'parsed_records' not in st.session_state:
    st.session_state.parsed_records = []
if 'selected_index' not in st.session_state:
    st.session_state.selected_index = None

# Step 1: PDF Upload
st.header("📤 Step 1: Upload PDF")
uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Upload a PDF file to parse and upload to Pinecone"
)

if uploaded_file is not None:
    st.success(f"✅ File uploaded: {uploaded_file.name}")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_file_path = tmp_file.name

    # Step 2: Parse with agentic_doc
    st.header("🔍 Step 2: Parse Document")
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("Parse PDF with agentic_doc", type="primary"):
            with st.spinner("Parsing document... This may take a few minutes."):
                try:
                    parsed_doc = parse(temp_file_path)
                    st.session_state.parsed_data = extract_json_from_parsed_doc(
                        parsed_doc)
                    st.write(st.session_state.parsed_data)

                except Exception as e:
                    st.error(f"❌ Error parsing document: {str(e)}")

    with col2:
        if st.session_state.parsed_data:
            st.info(f"📊 Parsing Results:")
            st.write(
                f"- **Total chunks:** {len(st.session_state.parsed_data.get('chunks', []))}")

    # Step 3: Prepare Records for Pinecone
    if st.session_state.parsed_data:
        st.header("📋 Step 3: Prepare Records")

        if st.button("Prepare Records for Pinecone"):
            records = parsed_doc_to_records(
                st.session_state.parsed_data, uploaded_file.name)

            st.session_state.parsed_records = records
            st.success(f"✅ Prepared {len(records)} records for upload")

        # Display prepared records
        if st.session_state.parsed_records:
            st.subheader("📋 Records Preview")

            # Create a DataFrame for better visualization
            df = pd.DataFrame(st.session_state.parsed_records)
            st.dataframe(
                df[['_id', 'chunk_text', 'chunk_type',
                    'pdf_filename', 'pdf_page', 'box']].head(10),
                use_container_width=True
            )

            if len(df) > 10:
                st.info(
                    f"Showing first 10 records out of {len(df)} total records")

            # # Show individual record details
            # selected_record_id = st.selectbox(
            #     "Select a record to view details:",
            #     options=[record['_id']
            #              for record in st.session_state.parsed_records],
            #     key="record_selector"
            # )

            # if selected_record_id:
            #     selected_record = next(
            #         (record for record in st.session_state.parsed_records if record['_id'] == selected_record_id),
            #         None
            #     )
            #     if selected_record:
            #         with st.expander("📄 Record Details", expanded=True):
            #             st.json(selected_record)

# Step 4: Pinecone Index Management
st.header("🗄️ Step 4: Pinecone Index Management")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Existing Indexes")
    try:
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]

        if index_names:
            selected_index = st.selectbox(
                "Select existing index:",
                options=index_names,
                key="existing_index_selector"
            )

            if selected_index:
                st.session_state.selected_index = selected_index

                # Show index stats
                if st.button("Show Index Stats"):
                    index = pc.Index(selected_index)
                    stats = index.describe_index_stats()
                    st.write(stats)
        else:
            st.info("No existing indexes found")

    except Exception as e:
        st.error(f"Error fetching indexes: {str(e)}")

with col2:
    st.subheader("➕ Create New Index")
    new_index_name = st.text_input(
        "New index name:", placeholder="my-document-index")

    # Model selection for index creation
    embedding_model = st.selectbox(
        "Select embedding model:",
        options=["multilingual-e5-large", "llama-text-embed-v2",
                 "pinecone-sparse-english-v0"],
        help="Choose the embedding model for your index"
    )

    if st.button("Create Index", type="primary"):
        if new_index_name:
            try:
                with st.spinner("Creating index..."):
                    # Create index with integrated inference
                    pc.create_index(
                        name=new_index_name,
                        dimension=1024,  # This will be set automatically based on the model
                        spec={
                            "serverless": {
                                "cloud": "aws",
                                "region": "us-east-1"
                            }
                        }
                    )

                    st.success(
                        f"✅ Index '{new_index_name}' created successfully!")
                    st.session_state.selected_index = new_index_name
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Error creating index: {str(e)}")
        else:
            st.warning("Please enter an index name")

# Step 5: Namespace Selection and Upload
if st.session_state.selected_index and st.session_state.parsed_records:
    st.header("🎯 Step 5: Namespace and Upload")

    col1, col2 = st.columns(2)

    with col1:
        # Namespace selection
        namespace = st.text_input(
            "Namespace:",
            value=uploaded_file.name.replace(
                '.pdf', '') if uploaded_file else "default",
            help="Namespace to organize your data within the index"
        )

    with col2:
        # Show existing namespaces
        try:
            index = pc.Index(st.session_state.selected_index)
            stats = index.describe_index_stats()
            existing_namespaces = list(stats.get('namespaces', {}).keys())

            if existing_namespaces:
                st.write("**Existing namespaces:**")
                for ns in existing_namespaces:
                    st.write(f"- {ns}")
            else:
                st.info("No existing namespaces")

        except Exception as e:
            st.error(f"Error fetching namespaces: {str(e)}")

    # Final upload section
    st.subheader("🚀 Upload to Pinecone")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write(f"**Ready to upload:**")
        st.write(f"- Index: `{st.session_state.selected_index}`")
        st.write(f"- Namespace: `{namespace}`")
        st.write(f"- Records: `{len(st.session_state.parsed_records)}`")

    with col2:
        if st.button("🚀 Upload to Pinecone", type="primary"):
            try:
                with st.spinner("Uploading to Pinecone..."):
                    index = pc.Index(st.session_state.selected_index)

                    # Upload records in batches (Pinecone limit is 96)
                    batch_size = 10  # Stay under the 96 limit
                    records = st.session_state.parsed_records

                    progress_bar = st.progress(0)

                    for i in range(0, len(records), batch_size):
                        batch = records[i:i + batch_size]

                        # Upload batch
                        index.upsert_records(namespace, batch)

                        # Update progress
                        progress = min((i + batch_size) / len(records), 1.0)
                        progress_bar.progress(progress)

                    progress_bar.progress(1.0)
                    st.success(
                        f"✅ Successfully uploaded {len(records)} records to Pinecone!")
                    st.balloons()

            except Exception as e:
                st.error(f"❌ Error uploading to Pinecone: {str(e)}")

# Cleanup section
if st.button("🧹 Clear Session Data"):
    st.session_state.parsed_data = None
    st.session_state.parsed_records = []
    st.session_state.selected_index = None
    st.success("Session data cleared!")
    st.rerun()

# Instructions and tips
with st.expander("💡 Instructions & Tips"):
    st.markdown("""
    ### How to use this tool:
    
    1. **Upload PDF**: Choose a PDF file from your computer
    2. **Parse Document**: Use agentic_doc to extract structured data from the PDF
    3. **Prepare Records**: Convert parsed data into Pinecone-compatible format
    4. **Manage Index**: Either select an existing Pinecone index or create a new one
    5. **Choose Namespace**: Select or create a namespace to organize your data
    6. **Upload**: Upload the prepared records to your Pinecone index
    
    ### Tips:
    - **Namespaces** help organize different documents within the same index
    - **Parsing** may take several minutes for large or complex PDFs
    - **Records** are automatically formatted with metadata for better retrieval
    - **Batching** ensures efficient upload of large document collections
    
    ### Environment Setup:
    Make sure you have set your `PINECONE_API_KEY` environment variable.
    """)
