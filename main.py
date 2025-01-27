from resources import read, write
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
from web_scraping import scrape_and_write_to_file,prepare_documents


def embed_documents_with_chroma(documents, persist_directory):
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    print(f'split docs first chunk = {split_docs[0]}')
    print(f'length of split docs = {len(split_docs)}')
    print(f'------------------------first chunk vector-----------------------------------------------------')
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    first_chunk = split_docs[0].page_content  
    vector = embeddings.embed_query(first_chunk)  
    print(f"First chunk embedding vector: {vector}")
    
    return Chroma.from_documents(split_docs, embeddings, persist_directory=persist_directory)

def main(links_file_path: str, base_dir: str, chroma_dir: str): 
    yaml_data = read.yaml_file(links_file_path)
    links = yaml_data.get("links", [])
    print(f'links in yaml file - {links}')
    scrape_and_write_to_file(links,base_dir)
    print(f'------------------------web scraping completed-----------------------------------------------------')
    documents = prepare_documents(base_dir)
    print(documents)
    print(f'------------------------doccuments completed-----------------------------------------------------')
    os.makedirs(chroma_dir, exist_ok=True)
    embed_documents_with_chroma(documents, chroma_dir)
   
if __name__=="__main__":
    links_file_path = "resources/links.yaml"
    base_dir = "markdown_files" 
    chroma_dir = "chroma_db"    
    main(links_file_path, base_dir, chroma_dir)  
