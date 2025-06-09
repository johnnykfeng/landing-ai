import json
import os
import tempfile
import pickle
from pathlib import Path
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

from agentic_doc.parse import parse
from agentic_doc.utils import viz_parsed_document
from agentic_doc.config import VisualizationConfig
from agentic_doc.common import ChunkType
from utils.serialization import save_pickle, save_json
from utils.file_utils import remove_extension
from utils.visualization import create_visualizations


if "parsed_documents" not in st.session_state:
    st.session_state["parsed_documents"] = None

PICKLE_DIR = Path("app_storage/parsed_docs_pkl")
JSON_DIR = Path("app_storage/parsed_docs_json")
VISUALIZATION_DIR = Path("app_storage/visualizations")

st.subheader("Load Parsed Documents")

if any(PICKLE_DIR.iterdir()):
    # st.info(f"Saved documents found in storage: {PICKLE_DIR.iterdir()}")
    # Create a dropdown for saved documents
    selected_file = st.selectbox(
        "Select a saved document to load",
        [file.name for file in PICKLE_DIR.iterdir()],
        key=f"selectbox_load_pickle"
    )

    if st.button("Load Parsed Documents"):
        st.write("Loading parsed documents...")
        try:
            with open(PICKLE_DIR / selected_file, "rb") as f:
                st.session_state["parsed_documents"] = pickle.load(f)
            with st.expander("Loaded Parsed Documents"):
                st.write(st.session_state["parsed_documents"])

        except Exception as e:
            st.error(f"Error loading parsed documents: {str(e)}")

if st.session_state["parsed_documents"] is not None:
    if st.button("Create Visualizations"):
        st.write("Creating visualizations...")
        output_dir = VISUALIZATION_DIR / remove_extension(selected_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        try:
            create_visualizations(st.session_state["parsed_documents"],
                                  doc_path=tmp_file_path,
                                  output_dir=output_dir)
            st.success("Visualizations created successfully")
        except Exception as e:
            st.error(f"Error creating visualizations: {str(e)}")

st.divider()
st.subheader("Visualize Parsed Documents")

if any(VISUALIZATION_DIR.iterdir()):
    st.info("Visualizations found in storage.")
    selected_folder = st.selectbox(
        "Select a folder to view visualizations",
        [folder.name for folder in VISUALIZATION_DIR.iterdir()],
        key="selectbox_folder"
    )

    selected_visualization = st.selectbox(
        "Select a visualization to view",
        [file.name for file in (VISUALIZATION_DIR / selected_folder).iterdir()],
        key=f"selectbox_{selected_folder}"
    )
    st.image(VISUALIZATION_DIR / selected_folder / selected_visualization)
else:
    st.info("No visualizations found in storage.")
