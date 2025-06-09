from pydantic import BaseModel, Field
from datetime import datetime

class Prompt(BaseModel):
    prompt_text: str = Field(description="The prompt text")
    model_name: str = Field(description="The LLM model this prompt is for")
    application: str = Field(description="The application this prompt is for")
    date_created: datetime = Field(description="The date the prompt was created")
    creator: str = Field(description="The creator of the prompt")
    

ANSWER_WITH_CONTEXT = Prompt(
    model_name="gpt-4o-mini",
    application="Answer with context for basic RAG",
    date_created=datetime(2025, 6, 8, 18, 30, 00),
    creator="John Feng",
    prompt_text="""\
Answer the question based on the context below.\n\
Context:\n\
{context}\n\n\
Question: {question}\n\
Answer:\
"""
)

SYSTEM_PROMPT = Prompt(
    model_name="gpt-4o-mini",
    application="System prompt for basic RAG",
    date_created=datetime(2025, 6, 8, 20, 30, 00),
    creator="John Feng",
    prompt_text="""\
You are a helpful assistant that can answer questions about the context provided."""
)

if __name__ == "__main__":
    print(ANSWER_WITH_CONTEXT.prompt_text.
          format(context="The moon is a big ball of rock and dust.", question="How big is the moon?"))

