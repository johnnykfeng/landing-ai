from pypdf import PdfReader, PdfWriter
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import os
import tempfile
from pathlib import Path

st.title("PDF Splitter")

uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

if uploaded_file is not None:
    # Create a temporary file to save the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, prefix=uploaded_file.name) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    # Read PDF
    reader = PdfReader(tmp_file_path)
    num_pages = len(reader.pages)

    st.write(f"PDF has {num_pages} pages")

    # Get page range from user
    col1, col2 = st.columns(2)
    with col1:
        start_page = st.number_input("Start Page", min_value=1, max_value=num_pages, value=1)
    with col2:
        end_page = st.number_input("End Page", min_value=start_page, max_value=num_pages, value=num_pages)

    if st.button("Split PDF"):
        writer = PdfWriter()

        # Add selected pages to writer
        for page_num in range(start_page-1, end_page):
            writer.add_page(reader.pages[page_num])

        # Create output filename
        output_filename = f"{Path(uploaded_file.name).stem}_pages_{start_page}_to_{end_page}.pdf"
        
        # Save split PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
            writer.write(tmp_output)
            tmp_output_path = tmp_output.name
        
        with st.expander("Preview Split PDF"):
            pdf_viewer(tmp_output_path)

        # Read the temporary file and create download button
        with open(tmp_output_path, "rb") as f:
            st.download_button(
                label="Download Split PDF",
                data=f,
                file_name=output_filename,
                mime="application/pdf"
            )

        # Clean up temporary files
        os.unlink(tmp_output_path)
    
    # Clean up input temporary file
    os.unlink(tmp_file_path)

st.divider() #-----------------------------------------------------

st.subheader("Merge PDFs")

# Allow multiple PDF uploads
uploaded_files = st.file_uploader("Upload PDFs to merge", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.write(f"Uploaded {len(uploaded_files)} PDFs")
    
    # Show uploaded files in order
    for i, pdf in enumerate(uploaded_files, 1):
        st.text(f"{i}. {pdf.name}")
    
    if st.button("Merge PDFs"):
        merger = PdfWriter()
        
        # Create temporary files for each uploaded PDF
        temp_files = []
        for pdf in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf.getvalue())
                temp_files.append(tmp_file.name)
        
        # Add all PDFs to merger
        for tmp_path in temp_files:
            merger.append(tmp_path)
            
        # Save merged PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
            merger.write(tmp_output)
            tmp_output_path = tmp_output.name
        
        with st.expander("Preview Merged PDF"):
            pdf_viewer(tmp_output_path)
            
        # Create output filename
        output_filename = "merged_pdf.pdf"
        
        # Read the temporary file and create download button
        with open(tmp_output_path, "rb") as f:
            st.download_button(
                label="Download Merged PDF",
                data=f,
                file_name=output_filename,
                mime="application/pdf"
            )
            
        # Clean up temporary files
        for tmp_path in temp_files:
            os.unlink(tmp_path)
        os.unlink(tmp_output_path)




