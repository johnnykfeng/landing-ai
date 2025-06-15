import os
from pathlib import Path
from typing import Tuple

# Corrected imports based on codebase search
from agentic_doc.utils import viz_parsed_document
from agentic_doc.config import VisualizationConfig
from agentic_doc.common import ChunkType
import cv2
import math
import pymupdf
import matplotlib.pyplot as plt
import numpy as np
import pickle
from utils.vector_db import get_box_from_chunk_ids
# from utils.vector_db import get_vector_db_as_df


def pdf_to_images(pdf_path):
    """
    Convert a PDF file to a list of images.
    Args:
        pdf_path (str): Path to the PDF file
    Returns:
        list: A list of images
    """
    doc = pymupdf.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap()
        # Convert PyMuPDF Pixmap to numpy array
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n)
        # Convert RGBA to RGB if needed
        if pix.n == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        images.append(img_array)
    return images


def _place_mark(
    img: np.ndarray,
    box_xyxy: tuple[int, int, int, int],
    text: str,
    *,
    color_bgr: tuple[int, int, int],
    viz_config: VisualizationConfig,
) -> None:
    text_color = color_bgr
    (text_width, text_height), baseline = cv2.getTextSize(
        text, viz_config.font, viz_config.font_scale, viz_config.thickness
    )
    text_x = int((box_xyxy[0] + box_xyxy[2] - text_width) // 2)
    text_y = int((box_xyxy[1] + box_xyxy[3] + text_height) // 2)

    # Draw the text background with opacity
    overlay = img.copy()
    cv2.rectangle(
        overlay,
        (text_x - viz_config.padding, text_y - text_height - viz_config.padding),
        (
            text_x + text_width + viz_config.padding,
            text_y + baseline + viz_config.padding,
        ),
        viz_config.text_bg_color,
        -1,
    )
    cv2.addWeighted(
        overlay, viz_config.text_bg_opacity, img, 1 - viz_config.text_bg_opacity, 0, img
    )

    # Draw the text on top
    cv2.putText(
        img,
        text,
        (text_x, text_y),
        viz_config.font,
        viz_config.font_scale,
        text_color,
        viz_config.thickness,
        cv2.LINE_AA,
    )
    # Draw the bounding box
    cv2.rectangle(img, box_xyxy[:2], box_xyxy[2:],
                  color_bgr, viz_config.thickness)



def create_visualizations(parsed_documents,
                          doc_path,
                          output_dir,
                          text_color=(0, 0, 255),
                          table_color=(0, 255, 0),
                          figure_color=(255, 0, 0),
                          marginalia_color=(0, 255, 255)):
    """
    Create visualizations for parsed documents.

    Args:
        parsed_documents: The parsed documents to visualize
        doc_path (str): Path to the original document
        output_dir (str): Directory to save visualizations
        text_color (Tuple[int, int, int]): RGB color for text chunks
        table_color (Tuple[int, int, int]): RGB color for table chunks
        figure_color (Tuple[int, int, int]): RGB color for figure chunks
        marginalia_color (Tuple[int, int, int]): RGB color for marginalia chunks

    Returns:
        str: The path to the output directory
    """
    # Check if output directory exists, if not create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    viz_config = VisualizationConfig(
        thickness=1,  # Thicker bounding boxes
        text_bg_opacity=0.5,  # More opaque text background
        font_scale=0.7,  # Larger text
        # Custom colors for different chunk types
        color_map={
            ChunkType.text: text_color,
            ChunkType.table: table_color,
            ChunkType.figure: figure_color,
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

def viz_grounding_box(img, chunk):
    viz_config = VisualizationConfig(
        thickness=2,  # Thicker bounding boxes
        text_bg_opacity=0.1,  # More opaque text background
        font_scale=0.7,  # Larger text
    )

    viz = img.copy()
    viz = cv2.cvtColor(viz, cv2.COLOR_RGB2BGR)
    height, width = img.shape[:2]
    for grounding in chunk.grounding:
        assert grounding.box is not None
        xmin, ymin, xmax, ymax = (
            max(0, math.floor(grounding.box.l * width)),
            max(0, math.floor(grounding.box.t * height)),
            min(width, math.ceil(grounding.box.r * width)),
            min(height, math.ceil(grounding.box.b * height)),
        )
        box = (xmin, ymin, xmax, ymax)
        _place_mark(
            viz,
            box,
            text=" ",
            color_bgr=viz_config.color_map[chunk.chunk_type],
            viz_config=viz_config,
        )

    viz = cv2.cvtColor(viz, cv2.COLOR_BGR2RGB)
    return viz

def viz_chunk_in_pdf(parsed_doc, pdf_filepath, chunk_id):
    """
    Visualize a chunk in a pdf.
    Args:
        parsed_doc: The parsed document
        pdf_filepath: The path to the pdf file
        chunk_id: The id of the chunk to visualize
    Returns:
        viz: nd.array image of page with chunk highlighted
    """
    images = pdf_to_images(pdf_filepath) # convert pdf pages to list of images
    try:
        chunk = next(c for c in parsed_doc[0].chunks if c.chunk_id == chunk_id) # get chunk from parsed doc
    except StopIteration:
        print(f"Chunk with id {chunk_id} not found in parsed doc")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    page_number = chunk.grounding[0].page # get page number from chunk
    img = images[page_number] # get image from list of images
    viz = viz_grounding_box(img, chunk) # visualize chunk in pdf
    return viz

def viz_chunk_with_box(box_json_list: list[dict], pdf_filepath: str):
    """
    Visualize a chunk in a pdf.
    Args:
        parsed_doc: The parsed document
        pdf_filepath: The path to the pdf file
        chunk_id: The id of the chunk to visualize
    Returns:
        viz: nd.array image of page with chunk highlighted
    """
    viz_config = VisualizationConfig(
        thickness=2,  # Thicker bounding boxes
        text_bg_opacity=0.1,  # More opaque text background
        font_scale=0.7,  # Larger text
    )
    images = pdf_to_images(pdf_filepath)
    for box_json in box_json_list:
        xmin, ymin, xmax, ymax = box_json['l'], box_json['t'], box_json['r'], box_json['b']
        box = (xmin, ymin, xmax, ymax)
        _place_mark(
            viz,
            box,
            text=" ",
            color_bgr=viz_config.color_map[ChunkType.text],
            viz_config=viz_config,
        )
    return viz

def draw_box_on_page(box_json: dict, 
                     img: np.ndarray, 
                     color: tuple[int, int, int] = (0, 255, 0), 
                     thickness: int = 2):
    """
    Draw a bounding box on an image and return the image.
    Returns:
        np.ndarray: Image with drawn bounding box
    """
    # Get image dimensions
    height, width = img.shape[:2]
    # Convert normalized coordinates to pixel coordinates
    xmin = int(box_json['l'] * width)
    ymin = int(box_json['t'] * height) 
    xmax = int(box_json['r'] * width)
    ymax = int(box_json['b'] * height)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) # convert to BGR for OpenCV
    img = cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, thickness)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

if __name__ == "__main__":
    pdf_filepath = r"C:\Users\johnk\Projects-code\LEARN\landing-ai\app_storage\original_files\Rejhon_2017_Semicond_Sci_Technol_32_085007.pdf"
    
    images = pdf_to_images(pdf_filepath)
    
    pickle_file = r"C:\Users\johnk\Projects-code\LEARN\landing-ai\app_storage\parsed_docs_pkl\Rejhon_2017_Semicond_Sci_Technol_32_085007.pkl"
    with open(pickle_file, 'rb') as f:
        parsed_doc = pickle.load(f)
    # chunk_id = "f35212f1-6bf0-4afc-a06a-5ea6552572fe"
    chunk_id = "f4485f40-ec21-43bc-982a-678e485e9ef7"
    viz = viz_chunk_in_pdf(parsed_doc, pdf_filepath, chunk_id)
    if viz is not None:
        plt.imshow(viz)
        plt.show()
    else:
        print(f"Chunk with id {chunk_id} not found in parsed doc")
    
        
 
