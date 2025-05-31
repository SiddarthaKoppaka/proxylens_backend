import json
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from src.utils.logging import log_event, track_time

# Initialize LLM for Answer Generation
local_llm = "llama3.1:8B"
llm = ChatOllama(model=local_llm, temperature=0)

# Conversational Answer Generation Prompt
generation_prompt = """You are a friendly and knowledgeable AI assistant engaged in a conversation. 
You have access to the **chat history**, the **retrieved information**, and the **current user question**.

**Chat History:**  
{history}

**Relevant Information Retrieved:**  
{context}

**User's Question:**  
{question}

### Guidelines:
- **Respond conversationally** as if you are having a natural discussion.
- **Avoid robotic phrases like "Based on the given context."** Instead, just answer directly.
- **If the retrieved context lacks enough details**, say what you do know, then invite the user to clarify.
- **Use past chat history** to maintain continuity and refer to past discussions naturally.
- **If the context contains extra details, provide only the most useful and interesting ones.**
- **Provide reference links at the end of the response if available.**
- *And Prettify your response***

### Response:
"""

def format_results(results):
    """
    Formats retrieved documents for better presentation to LLaMA and extracts reference links.

    Args:
        results (list): List of retrieved documents or search results.

    Returns:
        tuple: (Formatted text for LLaMA, List of reference links)
    """
    formatted_text = ""
    references = []

    for i, result in enumerate(results):
        if isinstance(result, dict):
            content = result.get("content", "No content available")
            metadata = result.get("metadata", {})

            # Extract possible reference links from metadata
            links = []
            for key, value in metadata.items():
                if isinstance(value, str) and value.startswith("http"):
                    links.append(value)

            # Append extracted links
            if links:
                references.extend(links)

            formatted_text += f"\n\n[{i+1}] {content}\nMetadata: {json.dumps(metadata, indent=2)}"

    return formatted_text.strip(), references

@track_time
def generate_answer(query, retrieved_data, session_id, chat_memory):
    """
    Uses LLaMA to generate a well-structured response based on chat history and retrieved results.

    Args:
        query (str): The user's question.
        retrieved_data (dict): Contains the source and results from `route_query()`.
        session_id (str): Session ID for tracking chat history.

    Returns:
        dict: Generated response with metadata and reference links.
    """
    source = retrieved_data["source"]
    results = retrieved_data["results"]

    # Format the retrieved data neatly and extract references
    formatted_context, references = format_results(results)

    # Retrieve chat history for continuity
    formatted_history = "\n".join([f"User: {entry['user']}\nAssistant: {entry['bot']}" for entry in chat_memory])

    # If no relevant results, return a fallback response
    if not formatted_context:
        response_text = "Hmm, I couldn't find much on that. Could you clarify or ask differently?"
        # chat_memory.setdefault(session_id, []).append({"user": query, "bot": response_text})
        return {
            "query": query,
            "source": source,
            "response": response_text,
            "references": []
        }

    # Generate the answer using LLaMA
    formatted_prompt = generation_prompt.format(history=formatted_history, context=formatted_context, question=query)
    response = llm.invoke([HumanMessage(content=formatted_prompt)])

    # Append references to the final response
    references_text = "\n\n**References:**\n" + "\n".join(references) if references else ""
    final_response = response.content + references_text

    log_event("Final Response", {"query": query, "source": source, "response": final_response, "references": references})

    return {
        "query": query,
        "source": source,
        "response": final_response,
        "references": references
    }
