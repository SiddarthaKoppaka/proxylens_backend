import json
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from src.utils.logging import log_event, track_time  # Import logging functions

# Initialize LLaMA in JSON mode for grading
local_llm = "llama3.1:8b"
llm_json_mode = ChatOllama(model=local_llm, temperature=0, format="json")

# Grading Instructions
retrieval_grader_prompt = """You are an expert at assessing the relevance of retrieved documents.

User Question: {query}

Here is a retrieved document:
{document}

Does this document contain useful information related to the question? 
Answer "yes" if relevant, "no" if irrelevant.

Return JSON with:
- `"binary_score"`: `"yes"` or `"no"` 
- `"relevance_score"`: A number from 0 to 1 (higher means more relevant)."""

@track_time
def grade_documents(query, retrieved_documents):
    """
    Grades each retrieved document to determine its relevance to the query.

    Args:
        query (str): User's query.
        retrieved_documents (list): List of retrieved documents from VectorStore.

    Returns:
        list: Only relevant documents.
    """
    relevant_documents = []
    total_docs = len(retrieved_documents)
    graded_results = []  # Store graded document scores

    for doc in retrieved_documents:
        if isinstance(doc, str):
            doc = {"content": doc}  # Convert string to dictionary format
        doc_content = doc.get("content", "")
        formatted_prompt = retrieval_grader_prompt.format(query=query, document=doc_content)

        response = llm_json_mode.invoke([SystemMessage(content="Assess the relevance"), HumanMessage(content=formatted_prompt)])

        try:
            grading_result = json.loads(response.content)
            score = grading_result.get("binary_score", "no")
            relevance = grading_result.get("relevance_score", 0.0)

            graded_results.append({"content": doc_content[:100], "score": score, "relevance": relevance})

            if score.lower() == "yes":
                relevant_documents.append(doc)

        except KeyError:
            continue  # Skip if there's an issue parsing

    # Log the results
    log_event("Retrieval Grading", {
        "query": query,
        "total_documents": total_docs,
        "relevant_documents": len(relevant_documents),
        "graded_results": graded_results
    })

    return relevant_documents




# class DocumentGrader:
#     def __init__(self, model_name="llama3.1:8b", temperature=0):
#         """
#         Initialize the DocumentGrader with a specific LLM model.
#         """
#         self.llm_json_mode = ChatOllama(model=model_name, temperature=temperature, format="json")
#         self.retrieval_grader_prompt = """You are an expert at assessing the relevance of retrieved documents.

# User Question: {query}

# Here is a retrieved document:
# {document}

# Does this document contain useful information related to the question? 
# Answer "yes" if relevant, "no" if irrelevant.

# Return JSON with:
# - `"binary_score"`: `"yes"` or `"no"` 
# - `"relevance_score"`: A number from 0 to 1 (higher means more relevant)."""

#     @track_time
#     def grade_documents(self, query, retrieved_documents):
#         """
#         Grades each retrieved document to determine its relevance to the query.

#         Args:
#             query (str): User's query.
#             retrieved_documents (list): List of retrieved documents from VectorStore.

#         Returns:
#             list: Only relevant documents.
#         """
#         relevant_documents = []
#         total_docs = len(retrieved_documents)
#         graded_results = []  # Store graded document scores

#         for doc in retrieved_documents:
#             if isinstance(doc, str):
#                 doc = {"content": doc}  # Convert string to dictionary format
#             doc_content = doc.get("content", "")
#             formatted_prompt = self.retrieval_grader_prompt.format(query=query, document=doc_content)

#             response = self.llm_json_mode.invoke([
#                 SystemMessage(content="Assess the relevance"),
#                 HumanMessage(content=formatted_prompt)
#             ])

#             try:
#                 grading_result = json.loads(response.content)
#                 score = grading_result.get("binary_score", "no")
#                 relevance = grading_result.get("relevance_score", 0.0)

#                 graded_results.append({"content": doc_content[:100], "score": score, "relevance": relevance})

#                 if score.lower() == "yes":
#                     relevant_documents.append(doc)

#             except KeyError:
#                 continue  # Skip if there's an issue parsing

#         # Log the results
#         log_event("Retrieval Grading", {
#             "query": query,
#             "total_documents": total_docs,
#             "relevant_documents": len(relevant_documents),
#             "graded_results": graded_results
#         })

#         return relevant_documents
