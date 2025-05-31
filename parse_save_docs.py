from agentic_doc.parse import parse_and_save_documents

# URLs to the document
documents = [
    "https://satsuite.collegeboard.org/media/pdf/sample-sat-score-report.pdf", 
    "https://www.rbcroyalbank.com/banking-services/_assets-custom/pdf/eStatement.pdf"
    ]

# Directory where the parsed results will be saved
result_save_dir = "./parsed_results"
grounding_save_dir = "./grounding"

# Parse the documents and save the results
result_paths = parse_and_save_documents(documents=documents, 
                                        result_save_dir=result_save_dir,
                                        grounding_save_dir=grounding_save_dir)

print(f"Result saved to: {result_paths}")


