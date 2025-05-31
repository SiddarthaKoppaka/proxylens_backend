import json
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, SystemMessage
from src.services.retriever import retriever_service
from src.services.metdata import lookup_metadata
from src.services.web_search import perform_web_search
from src.services.retrieval_grader import grade_documents
from src.db.chat_memory import get_chat_history, add_message
from src.utils.logging import log_event, track_time

# Initialize LLM for decision making
local_llm = "llama3.1:8b"
llm_json_mode = ChatOllama(model=local_llm, temperature=0, format="json")

# Define Tools

def retrieve_from_vectorstore(query: str):
    """Retrieve relevant documents from VectorStore."""
    vector_results = retriever_service.retrieve_documents(query)
    return grade_documents(query, vector_results)

def retrieve_from_metadata(query: str):
    """Retrieve structured metadata about a company."""
    return lookup_metadata(query)

def search_the_web(query: str):
    """Perform a web search for relevant information."""
    return perform_web_search(query)

vectorstore_tool = Tool(
    name="VectorStore Retriever",
    func=retrieve_from_vectorstore,
    description="Use this to retrieve financial reports, proxy reports, sales, or board members information."
)

metadata_tool = Tool(
    name="Metadata Lookup",
    func=retrieve_from_metadata,
    description="Use this to retrieve structured company information like company tickers, general details, or structured metadata."
)

websearch_tool = Tool(
    name="Web Search",
    func=search_the_web,
    description="Use this as a last resort when neither VectorStore nor Metadata provides relevant information."
)

# Initialize Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Define the Routing Agent
router_agent = initialize_agent(
    tools=[vectorstore_tool, metadata_tool, websearch_tool],
    llm=llm_json_mode,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,
)
@track_time
def route_query_agentic(query: str, session_id: str):
    """Agentic version of the router that dynamically decides the best retrieval method."""
    past_chats = get_chat_history(session_id)
    print(f"Chat History: {past_chats}")
    
    prompt = f"""
    Given the chat history: {past_chats}
    User Query: {query}
    
    Decide the best retrieval method:
    - Use **VectorStore** for financial reports, proxy reports, sales, or board members.
    - Use **Metadata Lookup** for structured company data.
    - Use **Web Search** if neither of the above is helpful.
    - Generate a Simple Response if the query doesn't contain enough context.

    Respond strictly in JSON format:
    {{
        "Thought": "Your reasoning here",
        "Action": "VectorStore Retriever | Metadata Lookup | Web Search | Generate Simple Response",
        "Action Input": "Refined query or additional request"
    }}
    """

    # Debugging: Print raw output
    raw_output = llm_json_mode.invoke(prompt)
    print(f"Raw LLM Output: {raw_output}")

    response = router_agent.invoke(prompt)  # Use invoke() instead of run()
    log_event("Agent Routing Decision", {"query": query, "response": response})
    return response
