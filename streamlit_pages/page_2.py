import streamlit as st

import os
from pathlib import Path

# st.set_page_config(
#     layout="wide",
#     page_title="App Storage Explorer",
#     page_icon=":material/edit:"
# )


st.title("App Storage Explorer")

# Define the storage directory
STORAGE_DIR = Path("app_storage")

# Check if directory exists
if not STORAGE_DIR.exists():
    st.error("Storage directory 'app_storage' not found!")
else:
    st.write("### Storage Directory Contents")

    # Create a tree-like view of the directory
    def explore_directory(directory, level=0):
        contents = []
        for item in directory.iterdir():
            if item.is_file():
                contents.append({level: " + "*level + "📄 " + item.name})
            elif item.is_dir():
                contents.append({level: " + "*level + "📁 " + item.name})
                contents.extend(explore_directory(item, level + 1))
        return contents

    # Display the directory contents
    directory_contents = explore_directory(STORAGE_DIR)
    # st.write(directory_contents)

    if not directory_contents:
        st.info("The storage directory is empty.")
    else:
        for item in directory_contents:
            if list(item.keys())[0] == 0:
                st.divider()
            for level, value in item.items():
                st.text(value)

    # Add some statistics
    total_files = len([f for f in STORAGE_DIR.rglob('*') if f.is_file()])
    total_dirs = len([d for d in STORAGE_DIR.rglob('*') if d.is_dir()])

    st.divider()
    st.write("### Storage Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Files", total_files)
    with col2:
        st.metric("Total Folders", total_dirs)
