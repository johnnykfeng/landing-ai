from pinecone import Pinecone, ServerlessSpec
import os
import sys
sys.path.append("C:/Users/johnk/Projects-code/LEARN/landing-ai")
from PROMPTS.prompts import ANSWER_WITH_CONTEXT
from openai import OpenAI
import pandas as pd
import json

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def create_index(index_name: str):
    """
    Create a new Pinecone index with the given name, dimension, and metric.
    """
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )
    
def json_to_string(json_obj):
    """Convert a Python dictionary to a string representation.

    Args:
        json_obj: Python dictionary to convert
    Returns:
        String representation of the dictionary
    """
    if isinstance(json_obj, dict):
        return json.dumps(json_obj)
    return str(json_obj)

def create_records(parsed_doc_json: dict, pdf_filename: str):
    """
    Create a list of records from a parsed document JSON object.
    """
    records = []
    for chunk in parsed_doc_json["chunks"]:
        record = {
            "_id": chunk["chunk_id"],
            "chunk_text": chunk["text"],
            "chunk_type": chunk["chunk_type"],
            "pdf_filename": pdf_filename,
            "pdf_page": chunk["grounding"][0]["page"],
            "box": json_to_string(chunk["grounding"][0]["box"])
        }
        records.append(record)
    return records

def query_to_embedding(query: str):
    """
    Create an embedding for a query using the OpenAI API.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    res = client.embeddings.create(
        model="text-embedding-ada-002",
        input=[query],
    )
    return res.data[0].embedding

def retrieve_contexts(query: str, index_name: str, namespace: str, top_k=2):
    """
    Retrieve contexts from a Pinecone index.
    """
    index = pc.Index(index_name)
    # xq = query_to_embedding(query)
    search_results = index.search(
        namespace = namespace,
        query={
            "top_k": top_k,
            "inputs": {
                'text': query
            }
        }
    )
    chunk_ids = [hit['_id'] for hit in search_results['result']['hits']]
    metadata_list = [hit['fields'] for hit in search_results['result']['hits']]
    return chunk_ids, metadata_list

def retrieval_augmented_prompt(context_list: list, query: str, context_limit=10000):
    """
    Retrieve contexts from a Pinecone index and return a prompt with the contexts.
    """
    # chunk_ids, metadata_list = retrieve_contexts(query, index_name, namespace, top_k, context_limit)
    # context_list = [metadata_list[i]['chunk_text'] for i in range(len(chunk_ids))]
    
    combined_contexts = []
    total_length = 0
    for context in context_list:
        new_length = total_length + len(context)
        if new_length >= context_limit:
            break
        combined_contexts.append(context)
        total_length = new_length
        
    total_context = "\n\n---\n\n".join(combined_contexts)
        
        
    prompt = ANSWER_WITH_CONTEXT.prompt_text.format(context=total_context, question=query)
    return prompt

def chat_response(prompt: str, model_name="gpt-4o-mini", temperature=0.1):
    """
    Send a prompt to the OpenAI API and return the response.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system_prompt = "You are a helpful assistant that can answer questions about the context provided."
    
    response = client.responses.create(
        model=model_name,
        instructions=system_prompt,
        input=prompt,
        temperature=temperature
    )
    return response.output_text

def rag_response(context_list: list, query: str, context_limit=10000):
    """
    Retrieve contexts from a Pinecone index and return a response using the OpenAI API.
    """
    prompt = retrieval_augmented_prompt(context_list, query, context_limit)
    return chat_response(prompt)


def get_vector_db_as_df(index_name: str, namespace: str) -> pd.DataFrame:
    """
    Fetch all vectors from a Pinecone index and namespace and return as a DataFrame.
    
    Args:
        index_name (str): Name of the Pinecone index
        namespace (str): Namespace within the index
        
    Returns:
        pd.DataFrame: DataFrame containing vector IDs, embeddings, and metadata
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)
    
    # Get all vector IDs in the namespace
    ids_batch = [id for id in index.list(namespace=namespace)][0]
    
    # Fetch vectors and metadata
    vectors_data = index.fetch(ids=ids_batch, namespace=namespace)
    vectors_dict = vectors_data.vectors
    
    # Convert to DataFrame format
    df_rows = []
    for vector_id, vector_data in vectors_dict.items():
        row = {
            'id': vector_id,
            'embedding': vector_data.values,
            'dimensions': len(vector_data.values),
            **vector_data.metadata
        }
        df_rows.append(row)
        
    df = pd.DataFrame(df_rows)
    
    # Convert pdf_page to int
    if 'pdf_page' in df.columns:
        df['pdf_page'] = df['pdf_page'].astype(int)
        
    return df

def get_box_from_chunk_ids(chunk_ids: list[str], namespace: str, index_name: str):
    """
    Get the box from a list of chunk IDs.
    """
    index = pc.Index(index_name)
    fetched_results = index.fetch(ids=chunk_ids, namespace=namespace)
    box_json_list = []
    for chunk_id in chunk_ids:
        box_json = fetched_results.vectors[chunk_id].metadata['box']
        box_json = json.loads(box_json)
        box_json_list.append(box_json)
    return box_json_list

def chunk_ids_to_pdf_pages(chunk_ids: list[str], namespace: str):
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)
    fetched_results = index.fetch(ids=chunk_ids, namespace=namespace)
    page_number_list = []
    for chunk_id in chunk_ids:
        page_number = fetched_results.vectors[chunk_id].metadata['pdf_page']
        page_number_list.append(page_number)
    return page_number_list

if __name__ == "__main__":
    questions = ["What is the experimental setup?", 
             "What is the conclusion of the paper?",
             "How is Schottky barrier formed?",
             "How is Schottky barrier height measured?",
             "How is Te02 thickness measured?",
             "How does Te02 thickness the performance of the detector?"]
    for question in questions[:4]:
        print("-"*50)
        print(f"Question: {question}")
        chunk_ids, metadata_list = retrieve_contexts(question, 'paper-chunks', 'Rejhon_2017_Semicond_Sci_Technol_32_085007')
        context_list = [metadata_list[i]['chunk_text'] for i in range(len(chunk_ids))]
        print(f"Chunk IDs: {chunk_ids}")
        # print(f"Metadata List: {metadata_list}")
        print(f"Answer: {rag_response(context_list, question)}")


