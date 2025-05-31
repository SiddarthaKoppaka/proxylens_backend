from fastapi import APIRouter, Query
from src.services.retriever import retriever_service
from src.services.router import route_query
from src.services.generator import generate_answer
from src.agents.rag_agent import route_query_agentic
from fastapi import HTTPException
from src.db.chat_memory import get_chat_history, add_message, get_all_chat_sessions

router = APIRouter()

@router.get("/search")
def search_vector_db(query: str = Query(..., description="Enter your query to search VectorDB")):
    """
    Directly queries the self-querying retriever (VectorStore) without routing.

    Returns:
        - query (str): The original user query.
        - results (list): Retrieved documents from the VectorStore.
    """
    results = retriever_service.retrieve_documents(query)
    return {"query": query, "results": results}


@router.get("/generate")
def generate_final_answer(query: str = Query(..., description="Enter your query for a structured response"),
                          session_id: str = Query(None, description="Session ID for maintaining chat context")):
    """
    Routes the query, retrieves relevant documents, and generates a structured response using LLaMA.
    Retrieves chat history if a session ID is provided.

    Returns:
        - query (str): The original user query.
        - source (str): The data source used.
        - response (str): The final generated response from LLaMA.
        - chat_history (list): Updated chat history for the session.
    """

    # Fetch chat history for context
    past_chats = get_chat_history(session_id)

    # Route the query with context from chat history
    retrieved_data = route_query(query, session_id, past_chats)

    # If it's a general response, return it directly without generating further responses
    if retrieved_data["source"] == "general_response":
        return {
            "query": query,
            "source": "general_response",
            "response": retrieved_data["response"],
            "chat_history": past_chats
        }

    # Generate response with history-aware refinement for non-general queries
    response = generate_answer(query, retrieved_data, session_id, past_chats)

    # Store the conversation
    add_message(session_id, query, response["response"])

    return {
        "query": query,
        "source": retrieved_data["source"],
        "response": response["response"],
        "chat_history": get_chat_history(session_id)
    }

@router.get("/chat-history")
def fetch_chat_sessions():
    """
    Retrieves all chat sessions with their titles and session IDs.
    This is used for displaying chat titles in the frontend navbar.
    """
    chat_sessions = get_all_chat_sessions()

    if not chat_sessions:
        return {"message": "No chat history available", "chat_sessions": []}

    return {"chat_sessions": chat_sessions}


@router.get("/agentic_rag/")
async def generate_response_agent(query: str, session_id: str):
    """
    Endpoint to generate a response using the agentic router.

    Args:
        query (str): The user's input query.
        session_id (str): The session ID for tracking chat history.

    Returns:
        JSON response with the retrieved information.
    """
    response = route_query_agentic(query, session_id)
    return {"query": query, "response": response}




@router.get("/chat-history/{session_id}")
def fetch_chat_history(session_id: str):
    """
    Retrieves the chat history for a specific session ID.
    This is used when a user selects a chat.
    """
    if not session_id:
        raise HTTPException(status_code=422, detail="Session ID is required")

    chat_data = get_chat_history(session_id)
    print(chat_data)

    if not chat_data:
        return {"message": "No messages found for this session", "chat_history": []}

    return {"session_id": session_id, "chat_history": chat_data}
