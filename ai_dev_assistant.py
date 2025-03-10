import os
import functools
import openai
import time
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

#global variables
CONTEXT = None
THREAD_ID = None  
CONTEXT_VERSION = 0 

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

def load_knowledge_base():
    global CONTEXT, THREAD_ID, CONTEXT_VERSION
    
    documents, skipped_files = load_documents_from_directory("knowledge_base")
    print(f"\nTotal documente încărcate: {len(documents)}")
    if skipped_files:
        print("\nFișiere sărite:")
        for file in skipped_files:
            print(f"- {file}")
    
    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    CONTEXT = "\n".join([doc.page_content for doc in documents])

    # Initialize thread once and send context
    openai.api_key = os.getenv("OPENAI_API_KEY")
    THREAD_ID = openai.beta.threads.create().id  

    openai.beta.threads.messages.create(
        thread_id=THREAD_ID,
        role="user",
        content=f"{CONTEXT}\n\nThis is the code context."
    )
    CONTEXT_VERSION += 1
    return CONTEXT

def openAiAnswer(prompt):
    global CONTEXT, THREAD_ID
    if CONTEXT is None:
        CONTEXT = load_knowledge_base()

    openai.api_key = os.getenv("OPENAI_API_KEY")
    assistant_id = os.getenv("ASSISTANT_ID")

    if not isinstance(prompt, str):
        raise ValueError("Prompt trebuie să fie un șir de caractere!")

    if THREAD_ID is None:
        THREAD_ID = openai.beta.threads.create().id  # Ensure thread exists

    # Add new message to the same thread (context is already known)
    openai.beta.threads.messages.create(
        thread_id=THREAD_ID,
        role="user",
        content=prompt
    )

    # Run the assistant
    run = openai.beta.threads.runs.create(
        thread_id=THREAD_ID,
        assistant_id=assistant_id
    )

    # Poll for the result (since assistant calls are async)
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=THREAD_ID, run_id=run.id)
        if run_status.status == "completed":
            break
        time.sleep(1)
    
    # Fetch messages from the thread
    messages = openai.beta.threads.messages.list(thread_id=THREAD_ID)
    
    # Return the last message (assistant response)
    return messages.data[0].content[0].text.value.strip()

@functools.lru_cache(maxsize=None)
def _askCodebase_cached(command, context_version):
    response = openAiAnswer(command)
    print("COMMAND: " + command)
    print("ANSWER: " + response)
    return response

def askCodebase(question):
    global CONTEXT_VERSION
    return _askCodebase_cached(question, CONTEXT_VERSION)
