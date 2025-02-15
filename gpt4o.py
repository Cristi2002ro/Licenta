import os
import constants 
import functools
import openai
import prompts
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

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
    # Încărcăm și procesăm documentele din întregul director
    documents, skipped_files = load_documents_from_directory("knowledge_base")
    print(f"\nTotal documente încărcate: {len(documents)}")
    if skipped_files:
        print("\nFișiere sărite:")
        for file in skipped_files:
            print(f"- {file}")

    # Împărțim textul în chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    context = "\n".join([doc.page_content for doc in documents])
    return context

def answer(prompt, context):
    openai.api_key = constants.APIKEY

    if not isinstance(context, str) or not isinstance(prompt, str):
        raise ValueError("Context și prompt trebuie să fie șiruri de caractere!")

    response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": prompts.system_context_propmt},
        {"role": "system", "content": context},
        {"role": "user", "content": prompt}
    ],
    temperature=0.4,  # Mai echilibrat
    top_p=0.85  # Reduce răspunsurile prea imprevizibile
    )

    return response.choices[0].message.content.strip() 

 
@functools.lru_cache(maxsize=None) 
def askCodebase(question):
    context = load_knowledge_base() 
    response = answer(question, context)
    print("CONTEXT: "+context) 
    print("QUESTION: "+ question)
    print("ANSWER: "+ response)
    return response
