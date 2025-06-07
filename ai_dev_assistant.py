import os
import functools
import openai
import time
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from session_manager import session_manager

def load_documents_from_directory(directory_path):
    documents = []
    skipped_files = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                print(f"Loading: {file_path}")
                loader = TextLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Could not load {file_path}: {str(e)}")
                skipped_files.append(file_path)
    
    return documents, skipped_files

def load_knowledge_base(session_id):
    session_dir = os.path.join("knowledge_base", session_id)
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
        
    documents, skipped_files = load_documents_from_directory(session_dir)
    print(f"\nTotal documents loaded for session {session_id}: {len(documents)}")
    if skipped_files:
        print("\nSkipped files:")
        for file in skipped_files:
            print(f"- {file}")
    
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    context = "\n".join([doc.page_content for doc in documents])

    openai.api_key = os.getenv("OPENAI_API_KEY")
    thread_id = openai.beta.threads.create().id

    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"{context}\n\nThis is the code context."
    )

    session_manager.create_session(session_id, context, thread_id)
    return context

def openAiAnswer(prompt, session_id):
    session = session_manager.get_session(session_id)
    if session is None:
        load_knowledge_base(session_id)
        session = session_manager.get_session(session_id)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    assistant_id = os.getenv("ASSISTANT_ID")

    if not isinstance(prompt, str):
        raise ValueError("Prompt must be a string!")

    thread_id = session["thread_id"]
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run_status.status == "completed":
            break
        time.sleep(1)
    
    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value.strip()

@functools.lru_cache(maxsize=None)
def _askCodebase_cached(command, session_id, version):
    response = openAiAnswer(command, session_id)
    print(f"COMMAND for session {session_id}: {command}")
    print("ANSWER: " + response)
    return response

def askCodebase(question, session_id):
    session = session_manager.get_session(session_id)
    version = session["version"] if session else 0
    return _askCodebase_cached(question, session_id, version)