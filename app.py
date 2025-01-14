import os
import constants 

from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI


os.environ["OPENAI_API_KEY"] = constants.APIKEY
# Configurăm embedding-urile
embeddings = OpenAIEmbeddings()

# Încărcăm și procesăm documentele
loader = TextLoader("data.txt")
documents = loader.load()

# Împărțim textul în chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

persist_directory = "chroma_db"

vectorstore = Chroma.from_documents(
    documents=texts,
    embedding=embeddings,
    persist_directory=persist_directory
)

vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)
retriever = vectorstore.as_retriever()

llm = OpenAI()

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

question= "Ce face functia train_model? explica cu bullet points"
response = qa_chain.run(question)

print("QUESTION: "+ question)
print("ANSWER: "+ response)