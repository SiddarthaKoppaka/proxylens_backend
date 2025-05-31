from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_ollama import ChatOllama
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

class SelfQueryRetrieverService:
    def __init__(self):
        """Initialize the retriever with embeddings, vector store, and metadata configuration."""
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

        # Connect to existing Qdrant collection
        self.vectorstore = QdrantVectorStore.from_existing_collection(
            embedding=self.embeddings,
            collection_name="proxy_chunks",
            url="http://ec2-52-90-231-181.compute-1.amazonaws.com:6333",
        )


        # Define metadata field information
        self.metadata_field_info = [
            AttributeInfo(name="company", description="The name of the company", type="string"),
            AttributeInfo(name="date", description="The financial report date in MM/DD/YYYY format", type="string"),
            AttributeInfo(name="year", description="The fiscal year of the report", type="integer"),
            AttributeInfo(name="tic", description="The stock ticker symbol of the company", type="string"),
            AttributeInfo(name="sale", description="Total sales or revenue of the company in million dollars", type="float"),
            AttributeInfo(name="cik", description="Central Index Key (CIK) assigned by the SEC", type="integer"),
            AttributeInfo(name="sic", description="Standard Industrial Classification (SIC) code for the company", type="integer"),
            AttributeInfo(name="annual_report_link", description="URL link to the company's annual report", type="string"),
            AttributeInfo(name="proxy_statement_link", description="URL link to the company's proxy statement", type="string"),
        ]

        # Define document content description
        self.document_content_description = "Financial report details of a company"

        # Initialize the language model
        self.llm = ChatOllama(model="llama3", temperature=0)

        # Create the SelfQueryRetriever
        self.retriever = SelfQueryRetriever.from_llm(
            llm=self.llm,
            vectorstore=self.vectorstore,
            document_contents=self.document_content_description,
            metadata_field_info=self.metadata_field_info,
        )

    def retrieve_documents(self, query: str):
        """Retrieve relevant documents based on a self-querying mechanism."""
        try:
            documents = self.retriever.invoke(query)
            return [{"content": doc.page_content, "metadata": doc.metadata} for doc in documents]
        except Exception as e:
            return {"error": f"Retrieval failed: {str(e)}"}

# Create a single instance of the retriever service
retriever_service = SelfQueryRetrieverService()
