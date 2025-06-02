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


def remove_extension(file_name):
    return file_name.split('.')[0]


def save_pickle(parsed_documents, save_dir, file_name):
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    file_name = remove_extension(file_name) + '.pkl'
    file_path = save_dir / file_name
    with open(file_path, "wb") as f:
        pickle.dump(parsed_documents, f)
    return file_path


def create_visualizations(parsed_documents,
                          doc_path,
                          output_dir,
                          text_color=(0, 0, 255),
                          table_color=(0, 255, 0),
                          figure_color=(255, 0, 0),
                          marginalia_color=(0, 255, 255)):

    # Check if output directory exists, if not create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    viz_config = VisualizationConfig(
        thickness=1,  # Thicker bounding boxes
        text_bg_opacity=0.5,  # More opaque text background
        font_scale=0.7,  # Larger text
        # Custom colors for different chunk types
        color_map={
            ChunkType.text: text_color,  # Red for tables
            ChunkType.table: table_color,  # Green for tables
            ChunkType.figure: figure_color,  # Blue for text
            ChunkType.marginalia: marginalia_color
        }
    )

    for parsed_doc in parsed_documents:
        images = viz_parsed_document(
            doc_path,
            parsed_doc,
            output_dir=output_dir,
            viz_config=viz_config
        )

    return output_dir


if "parsed_documents" not in st.session_state:
    st.session_state["parsed_documents"] = None

PICKLE_DIR = Path("app_storage/parsed_docs_pkl")
RESULT_SAVE_DIR = Path("app_storage/parsed_docs_json")
VISUALIZATION_DIR = Path("app_storage/visualizations")


st.title("Agentic Document Parser")

uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

if uploaded_file is not None:
    # Create a temporary file to save the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, prefix=uploaded_file.name) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    with st.expander("Uploaded PDF Preview"):
        try:
            pdf_viewer(tmp_file_path)
        except Exception as e:
            st.error(f"Error loading PDF: {str(e)}")

    # save_results = st.checkbox("Save Parsed Results", value=True)
    if st.button("Parse PDF"):
        st.write("Parsing PDF...")
        try:
            st.session_state["parsed_documents"] = parse(tmp_file_path)
            st.success("PDF parsed successfully")
        except Exception as e:
            st.error(f"Error parsing PDF: {str(e)}")

    if st.session_state["parsed_documents"] is not None:
        with st.expander("Parsed Documents"):
            st.write(st.session_state["parsed_documents"])

        if st.button("Save Parsed Documents"):
            st.write("Saving parsed documents...")
            try:
                save_pickle(st.session_state["parsed_documents"],
                            save_dir=PICKLE_DIR,
                            file_name=uploaded_file.name)
                st.success("Parsed documents saved successfully")
            except Exception as e:
                st.error(f"Error saving parsed documents: {str(e)}")

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
