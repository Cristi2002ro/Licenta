import os
import constants 

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter



os.environ["OPENAI_API_KEY"] = constants.APIKEY
# Configurăm embedding-urile
embeddings = OpenAIEmbeddings()

# Încărcăm și procesăm documentele
loader = TextLoader("data.txt")  # Înlocuiește cu calea corectă
documents = loader.load()

# Împărțim textul în chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# Creăm și persistăm vectorstore-ul folosind Chroma
# Specificăm un director pentru persistență
persist_directory = "chroma_db"

vectorstore = Chroma.from_documents(
    documents=texts,
    embedding=embeddings,
    persist_directory=persist_directory
)

# Important: Salvăm explicit vectorstore-ul
vectorstore.persist()

# Pentru a încărca ulterior vectorstore-ul existent
vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

# Creăm retriever-ul
retriever = vectorstore.as_retriever()

# Creăm lanțul RetrievalQA
from langchain.llms import OpenAI
llm = OpenAI()  # sau alt model de limbaj la alegere

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

# Execută interogări
response = qa_chain.run("Ce face functia preprocess_text? explica cu bullet points")
print("ANSWER: "+ response)