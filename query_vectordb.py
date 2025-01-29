from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import asyncio


def get_vectorstore():
    
    if not hasattr(get_vectorstore, "vectorstore"):
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        persist_directory = "chroma_db"
        get_vectorstore.vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)
    return get_vectorstore.vectorstore

async def generate_vector_db_response(prompt):
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(prompt, k=5)
    response = [result.page_content for result in results]
    for idx, result in enumerate(results, start=1):
         print(f'----------------------------START of content:{idx} ----------------------------')
         print(result.page_content)
         print(f'----------------------------END of content:{idx} ----------------------------')
    
    return response

if __name__=="__main__":
    asyncio.run(generate_vector_db_response("what are the contact us")) 