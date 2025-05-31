import os
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Retrieve API key from environment variables
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Ensure the API key is available
if not TAVILY_API_KEY:
    raise ValueError("Missing TAVILY_API_KEY. Make sure it's set in the .env file.")

# Initialize Tavily Web Search Client
client = TavilyClient(TAVILY_API_KEY)

def perform_web_search(query: str):
    """
    Perform a web search using the Tavily API.

    Args:
        query (str): The search query.

    Returns:
        list: A list of relevant search results.
    """
    try:
        response = client.search(query=query)
        return response.get("results", [])  # Extract results from response
    except Exception as e:
        return {"error": f"Web search failed: {str(e)}"}


# import os
# from tavily import TavilyClient
# from dotenv import load_dotenv

# class WebSearchTool:
#     def __init__(self):
#         """
#         Initialize the WebSearchTool by loading API keys and setting up the Tavily client.
#         """
#         load_dotenv()
#         self.api_key = os.getenv("TAVILY_API_KEY")

#         if not self.api_key:
#             raise ValueError("Missing TAVILY_API_KEY. Make sure it's set in the .env file.")

#         self.client = TavilyClient(self.api_key)

#     def perform_web_search(self, query: str):
#         """
#         Perform a web search using the Tavily API.

#         Args:
#             query (str): The search query.

#         Returns:
#             list: A list of relevant search results or an error message.
#         """
#         try:
#             response = self.client.search(query=query)
#             return response.get("results", [])  # Extract results from response
#         except Exception as e:
#             return {"error": f"Web search failed: {str(e)}"}
