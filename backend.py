import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceHub
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

load_dotenv()
os.environ['HUGGINGFACEHUB_API_TOKEN'] = "YOUR API KEY"

class CustomDocument:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

    def __repr__(self):
        return f"CustomDocument(content_length={len(self.page_content)}, metadata={self.metadata})"

    def to_dict(self):
        return {
            "page_content": self.page_content,
            "metadata": self.metadata
        }

class PyPDFDirectoryLoader:
    def __init__(self, path):
        self.path = path

    def load(self):
        documents = []
        try:
            reader = PdfReader(self.path)
            number_of_pages = len(reader.pages)
            content = ""
            for page_num in range(number_of_pages):
                page = reader.pages[page_num]
                content += page.extract_text()
            documents.append(CustomDocument(page_content=content))
        except Exception as e:
            print(f"Error reading PDF file: {e}")
        return documents

def response(user_query):
    huggingface_embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    loader = PyPDFDirectoryLoader("FINAL_SCRAPED_DATA.pdf")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(documents)
    vectorstore = FAISS.from_documents(final_documents[:120], huggingface_embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    llm = HuggingFaceHub(
        repo_id="mistralai/Mistral-7B-v0.1",
        model_kwargs={"temperature": 0.1, "max_length": 500}
    )

    template = """Please use the following pieces of context to answer the question at the end.
    Say that you don't know when asked a question you don't know, do not make up an answer. Be precise and concise in your answer.

    {context}

    Question: {question}

    Answer:"""

    custom_rag_prompt = PromptTemplate.from_template(template)

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": custom_rag_prompt}
    )

    result = rag_chain.invoke(user_query)
    
    answer = result['result'].split("Answer:")[-1].strip()
    response_dict = {"answer": answer}

    return response_dict

