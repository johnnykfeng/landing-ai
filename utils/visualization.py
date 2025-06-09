import os
from pathlib import Path
from typing import Tuple

# Corrected imports based on codebase search
from agentic_doc.utils import viz_parsed_document
from agentic_doc.config import VisualizationConfig
from agentic_doc.common import ChunkType


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
