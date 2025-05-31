import json
from src.services.retriever import retriever_service
from src.services.metdata import lookup_metadata
from src.services.web_search import perform_web_search
from src.services.retrieval_grader import grade_documents
from src.db.chat_memory import get_chat_history, add_message
from langchain_core.messages import HumanMessage, SystemMessage
from src.utils.logging import log_event, track_time
from langchain_ollama import ChatOllama

# Initialize LLM for Routing
local_llm = "llama3.1:8b"
llm_json_mode = ChatOllama(model=local_llm, temperature=0, format="json")

# Enhanced Routing Instructions with General Response Handling
router_instructions = """You are an advanced routing and query refinement assistant.
Your job is to:
1. **Determine the best retrieval method** from:
   - **VectorStore**: Contains financial reports, proxy reports, employee data, board members, people, names, executive members and sales data.
   - **Metadata Lookup**: Contains structured company info (company names, years, ticker symbols).
   - **Web Search**: If neither of the above sources provide relevant information.
   - **General Response**: If the query does not require any retrieval, answer directly.

2. **Prioritize VectorStore Retrieval**:
   - If the user asks about **financial reports, proxy reports, sales, or board members**, **VectorStore should be the primary source**.
   - Use **Metadata Lookup** only for structured queries like company tickers or general info.
   - Use **Web Search ONLY IF** neither VectorStore nor Metadata provides relevant results.

3. **Refine the query intelligently**:
   - **Use past chat history** to make the query more specific.
   - **If the user references an earlier company/entity without naming it**, infer what they mean based on past messages.
   - **Eliminate unnecessary words & improve query structure** to make retrieval more effective.

4. **Handle General Responses**:
    - **If the query is a general question (not requiring search), generate a response directly**.
    - **Provide a helpful, concise, and relevant answer**.
    - **DO NOT perform any retrieval for general queries**.

### **Routing Decision Format (Return JSON)**
- `"datasource"`: `"vectorstore"`, `"metadata"`, `"websearch"`, or `"general_response"`
- `"updated_query"`: **A refined version of the query using chat history, If there is Chat History OR else return the given query**
- `"general_response"`: **Response for general queries only**
"""

@track_time
def route_query(query: str, session_id: str, past_chats: list):
    """
    Routes the query to the correct retrieval method, incorporating chat history.

    Args:
        query (str): The user's question.
        session_id (str): The session ID for tracking chat history.

    Returns:
        dict: Retrieved and filtered results from the correct source.
    """

    # Retrieve chat history
    print(f"Chat History: {past_chats}")

    # Pass chat history to the router LLM for query refinement
    routing_decision = llm_json_mode.invoke([
        SystemMessage(content=router_instructions),
        HumanMessage(content=f"Chat History: {past_chats}\n\nUser Query: {query}")
    ])

    try:
        decision_data = json.loads(routing_decision.content)
        datasource = decision_data["datasource"]
        updated_query = decision_data["updated_query"]
        general_response = decision_data.get("general_response", None)
    except (KeyError, json.JSONDecodeError):
        datasource = "vectorstore"  # Default fallback to prioritize VectorStore
        updated_query = query
        general_response = None

    print(f"Routing Decision: {datasource} | Updated Query: {updated_query} | general_response : {general_response if (general_response) else 'None'}")
    log_event("Routing Decision", {"query": query, "chosen_source": datasource, "updated_query": updated_query})

    # If it's a general response, return the generated response directly
    if datasource == "general_response" and general_response:
        return {
            "source": "general_response",
            "query": updated_query,
            "response": general_response
        }

    # Try VectorStore Retrieval First
    vector_results = retriever_service.retrieve_documents(updated_query)

    # Extract relevant documents via grading
    relevant_results = grade_documents(updated_query, vector_results)

    # Extract annual and proxy statement links (if available)
    annual_report_links = []
    proxy_statement_links = []

    for doc in relevant_results:
        metadata = doc.get("metadata", {})
        if "annualreport" in metadata:
            annual_report_links.append(metadata["annualreport"])
        if "proxystatement" in metadata:
            proxy_statement_links.append(metadata["proxystatement"])

    if relevant_results:
        return {
            "source": "vectorstore",
            "query": updated_query,
            "results": relevant_results,
            "annual_reports": annual_report_links,
            "proxy_statements": proxy_statement_links
        }

    # If VectorStore Results are Irrelevant, Try Metadata Lookup
    metadata_results = lookup_metadata(updated_query)
    if metadata_results:
        return {
            "source": "metadata",
            "query": updated_query,
            "results": metadata_results,
            "annual_reports": [],
            "proxy_statements": []
        }

    # If No Relevant Data, Use Web Search as Last Resort
    web_results = perform_web_search(updated_query)
    return {
        "source": "websearch",
        "query": updated_query,
        "results": web_results,
        "annual_reports": [],
        "proxy_statements": []
    }