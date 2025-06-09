import pickle
import json
from pathlib import Path

from .file_utils import remove_extension


def save_pickle(parsed_documents, save_dir, file_name):
    """
    Save documents as a pickle file.

    Args:
        parsed_documents: The documents to save
        save_dir (str): The directory to save to
        file_name (str): The name for the file

    Returns:
        Path: The path to the saved file
    """
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    file_name = remove_extension(file_name) + '.pkl'
    file_path = save_dir / file_name
    with open(file_path, "wb") as f:
        pickle.dump(parsed_documents, f)
    return file_path


def save_json(parsed_results, doc_path, save_dir):
    """
    Save parsed results as a JSON file.

    Args:
        parsed_results: The results to save
        doc_path (str): The path to the source document
        save_dir (str): The directory to save to

    Returns:
        tuple: The JSON data and the path to the saved file
    """
    # Create json save directory if it doesn't exist
    json_save_dir = Path(save_dir)
    json_save_dir.mkdir(parents=True, exist_ok=True)

    # Create json filename from doc path
    json_file_name = Path(doc_path).stem + ".json"
    json_file_path = json_save_dir / json_file_name

    # Convert parsed results to json-serializable format
    json_data = {
        "markdown": parsed_results[0].markdown,
        "chunks": [
            {
                "text": chunk.text,
                "grounding": [
                    {
                        "page": g.page,
                        "box": {
                            "l": g.box.l,
                            "t": g.box.t,
                            "r": g.box.r,
                            "b": g.box.b
                        },
                        "image_path": g.image_path
                    } for g in chunk.grounding
                ],
                "chunk_type": chunk.chunk_type,
                "chunk_id": chunk.chunk_id
            } for chunk in parsed_results[0].chunks
        ],
        "start_page_idx": parsed_results[0].start_page_idx,
        "end_page_idx": parsed_results[0].end_page_idx,
        "doc_type": parsed_results[0].doc_type,
        "result_path": parsed_results[0].result_path,
        "errors": parsed_results[0].errors
    }

    # Save as json file
    with open(json_file_path, 'w') as f:
        json.dump(json_data, f, indent=2)

    return json_data, json_file_path
