from agentic_doc.parse import parse_documents
from agentic_doc.utils import viz_parsed_document
# from agentic_doc.utils import ChunkType
from agentic_doc.common import ChunkType
from agentic_doc.config import VisualizationConfig

doc_path = "John Feng Resume Hard Tech 2025-05-25.pdf"

# Parse a document
results = parse_documents([doc_path])

parsed_doc = results[0]

# Create visualizations with default settings
# The output images have a PIL.Image.Image type
images = viz_parsed_document(
    doc_path,
    parsed_doc,
    output_dir="viz"
)

# Or customize the visualization appearance
viz_config = VisualizationConfig(
    thickness=2,  # Thicker bounding boxes
    text_bg_opacity=0.8,  # More opaque text background
    font_scale=0.7,  # Larger text
    # Custom colors for different chunk types
    color_map={
        ChunkType.figure: (0, 0, 255),  # Red for tables
        ChunkType.text: (255, 0, 0),  # Blue for regular text
        # ... other chunk types ...
    }
)

images = viz_parsed_document(
    doc_path,
    parsed_doc,
    output_dir="visualizations",
    viz_config=viz_config
)

# The visualization images will be saved as:
# path/to/save/visualizations/document_viz_page_X.png
# Where X is the page number