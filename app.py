import os
import constants 

from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI

os.environ["OPENAI_API_KEY"] = constants.APIKEY
embeddings = OpenAIEmbeddings()

def load_documents_from_directory(directory_path):
    documents = []
    skipped_files = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                print(f"Încărcare: {file_path}")
                loader = TextLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Nu s-a putut încărca {file_path}: {str(e)}")
                skipped_files.append(file_path)
    
    return documents, skipped_files

def init_knowledgebase():
# Încărcăm și procesăm documentele din întregul director
    documents, skipped_files = load_documents_from_directory("knowledge_base")
    print(f"\nTotal documente încărcate: {len(documents)}")
    if skipped_files:
        print("\nFișiere sărite:")
        for file in skipped_files:
            print(f"- {file}")

    # Împărțim textul în chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    persist_directory = "chroma_db"

    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    retriever = vectorstore.as_retriever()

    llm = OpenAI()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )
    return qa_chain

def askCodebase(question):
    qa_chain=init_knowledgebase()
    response = qa_chain.run(question)
    print("QUESTION: "+ question)
    print("ANSWER: "+ response)
    return response