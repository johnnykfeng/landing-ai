# 🤖📄 Agentic Document Parser with Pinecone RAG

A comprehensive document intelligence platform that combines advanced PDF parsing capabilities with semantic search and retrieval-augmented generation (RAG). This application leverages the power of [agentic-doc](https://github.com/agentic-doc/agentic-doc) for intelligent document parsing and Pinecone for vector-based document retrieval.

## ✨ Features

### 📄 Agentic Document Parser
- **Advanced PDF Parsing**: Intelligent extraction of text, tables, figures, and marginalia from PDF documents
- **Visual Grounding**: Precise bounding box detection and visualization of extracted content
- **Multiple Export Formats**: Save parsed results as JSON or pickle files
- **Visual Annotations**: Generate annotated PDF visualizations with color-coded content types

### 🔍 Pinecone RAG System
- **Semantic Search**: Query documents using natural language with vector similarity search
- **Visual Context**: View search results with highlighted regions in original PDF documents
- **Flexible Filtering**: Filter results by content type (text, tables, figures, marginalia)
- **Multi-Model Support**: Choose from multiple AI models for response generation (GPT-4o, GPT-4o-mini)

### 📤 Data Upload Pipeline
- **Seamless Integration**: Parse PDFs and upload directly to Pinecone vector database
- **Index Management**: Create and manage Pinecone indexes with integrated inference
- **Namespace Organization**: Organize documents using namespaces for better data management
- **Batch Processing**: Handle multiple documents efficiently

### ✂️ PDF Utilities
- **PDF Splitting**: Extract specific page ranges from PDF documents
- **PDF Merging**: Combine multiple PDF files into a single document
- **Preview Interface**: View PDF content before processing

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) - Interactive web application framework
- **Document Parsing**: [agentic-doc](https://github.com/agentic-doc/agentic-doc) - Advanced document parsing and analysis
- **Vector Database**: [Pinecone](https://www.pinecone.io/) - Scalable vector database for semantic search
- **PDF Processing**: [PyPDF](https://pypdf.readthedocs.io/) - PDF manipulation and processing
- **AI Integration**: OpenAI API for natural language processing and generation
- **Visualization**: OpenCV and PIL for image processing and visualization

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Pinecone API key
- OpenAI API key
- UV package manager (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd landing-ai
   ```

2. **Install dependencies**
   
   Using UV (recommended):
   ```bash
   uv sync
   ```
   
   Using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   PINECONE_API_KEY=your_pinecone_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   
   Navigate to `http://localhost:8501` to access the application.

## 📖 Usage Guide

### 1. Document Parsing

1. Navigate to the "📄 Agentic Doc Parser" tab
2. Upload a PDF file using the file uploader
3. Click "Parse PDF" to extract content with intelligent analysis
4. Save parsed results for future use
5. Generate visual annotations to see bounding boxes for different content types

### 2. Upload to Pinecone

1. Go to the "📤 Pinecone Data Upload" tab
2. Upload and parse a PDF document
3. Select or create a Pinecone index
4. Choose a namespace for organization
5. Upload processed data to your vector database

### 3. Semantic Search & RAG

1. Access the "🔍 Pinecone RAG" tab
2. Select your index and namespace
3. Enter a natural language query
4. Filter by content types (text, figures, tables, marginalia)
5. Review search results with visual context
6. Generate AI-powered responses using retrieved context

### 4. PDF Utilities

1. Use the "✂️ PDF Split & Merge" tab for:
   - Splitting PDFs by page ranges
   - Merging multiple PDFs into one
   - Previewing results before download

## 📁 Project Structure

```
landing-ai/
├── app.py                          # Main Streamlit application
├── streamlit_pages/                # Individual app pages
│   ├── agentic_doc_app.py         # Document parsing interface
│   ├── pinecone_upload.py         # Data upload pipeline
│   ├── pinecone_rag.py            # RAG and search interface
│   └── pdf_split_merge.py         # PDF utilities
├── utils/                          # Utility modules
│   ├── vector_db.py               # Vector database operations
│   ├── visualization.py           # Image processing and visualization
│   ├── serialization.py           # Data serialization utilities
│   └── file_utils.py              # File handling utilities
├── app_storage/                    # Local storage for processed files
│   ├── parsed_docs_pkl/           # Pickle files of parsed documents
│   ├── parsed_docs_json/          # JSON exports
│   ├── visualizations/            # Generated visualizations
│   └── original_files/            # Original PDF files
├── notebooks/                      # Jupyter notebooks for development
├── Pinecone_Tutorial/             # Tutorial and example code
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🔧 Configuration

### Streamlit Configuration

The application uses custom Streamlit configuration located in `.streamlit/config.toml`. You can modify this file to customize the application's appearance and behavior.

### Environment Variables

Required environment variables:
- `PINECONE_API_KEY`: Your Pinecone API key
- `OPENAI_API_KEY`: Your OpenAI API key

## 🧪 Development

### Running in Development Mode

```bash
# Install development dependencies
uv sync --dev

# Run with hot reload
streamlit run app.py --server.runOnSave true
```

### Code Quality

The project uses Ruff for linting and formatting:

```bash
# Run linting
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

## 📚 API Reference

### Pinecone Integration

The application supports multiple Pinecone embedding models:
- `multilingual-e5-large`: Efficient multilingual embeddings
- `llama-text-embed-v2`: High-performance text embeddings  
- `pinecone-sparse-english-v0`: Sparse embeddings for keyword search

### OpenAI Models

Supported models for RAG responses:
- `gpt-4o`: Advanced reasoning and generation
- `gpt-4o-mini`: Faster, cost-effective alternative

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

If you encounter any issues or have questions:

1. Check the [TODO.md](TODO.md) file for known issues and planned features
2. Open an issue on GitHub
3. Refer to the documentation of underlying libraries:
   - [agentic-doc documentation](https://github.com/agentic-doc/agentic-doc)
   - [Pinecone documentation](https://docs.pinecone.io/)
   - [Streamlit documentation](https://docs.streamlit.io/)

## 🚧 Roadmap

See [TODO.md](TODO.md) for planned features and improvements including:
- Resume and cover letter search functionality
- Enhanced scientific paper processing
- Authentication system for multi-user support
- Advanced visualization capabilities

---

Built with ❤️ using Streamlit, agentic-doc, and Pinecone
