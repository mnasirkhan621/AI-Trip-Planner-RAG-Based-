import os
import json
import ast
from datasets import load_dataset
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# Configuration
DATASET_NAME = "osunlp/TravelPlanner"
PERSIST_DIRECTORY = os.path.join(os.getcwd(), "data", "chroma_db")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

def ingest():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # 1. Load Dataset
    print(f"Downloading {DATASET_NAME}...")
    try:
        # The dataset requires a configuration name, e.g., 'train'
        dataset_dict = load_dataset(DATASET_NAME, "train")
        print(f"Loaded dataset keys: {dataset_dict.keys()}")
        
        # Access the split
        if 'train' in dataset_dict:
            dataset = dataset_dict['train']
        else:
            first_split = list(dataset_dict.keys())[0]
            print(f"Using split: {first_split}")
            dataset = dataset_dict[first_split]
            
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # 2. Extract Reference Information
    restaurants_map = {}
    hotels_map = {}
    attractions_map = {}
    
    print("Extracting reference information...")
    count = 0
    
    for entry in dataset:
        ref_info = entry.get('reference_information')
        if not ref_info:
            continue
            
        # Parse if string (handle potential double encoding and single quotes)
        max_depth = 3
        while isinstance(ref_info, str) and max_depth > 0:
            try:
                ref_info = json.loads(ref_info)
            except json.JSONDecodeError:
                try:
                    ref_info = ast.literal_eval(ref_info)
                except Exception:
                    # Only print verbose error for first few failures or if critical
                    if count < 5: 
                        print(f"Failed to parse reference_information JSON/Literal. Content partial: {ref_info[:50]}...")
                    break
            max_depth -= 1
        
        if isinstance(ref_info, list):
            # Inspect structure - The logs showed [{'Description': '...', 'Content': '...'}]
            for item in ref_info:
                if isinstance(item, dict):
                    # Check for 'Content' which likely holds the actual data
                    content_blob = item.get('Content')
                    if content_blob:
                        # 'Content' might be a stringified JSON or just text.
                        # Given the errors earlier, it's likely the string we need to parse.
                        parsed_content = content_blob
                        if isinstance(content_blob, str):
                            try:
                                parsed_content = json.loads(content_blob)
                            except json.JSONDecodeError:
                                try:
                                    parsed_content = ast.literal_eval(content_blob)
                                except Exception:
                                    if count < 5:
                                        print(f"Failed to parse Content string: {content_blob[:50]}...")
                                    continue
                        
                        # Now parsed_content should have the keys we want
                        if isinstance(parsed_content, dict):
                            if 'restaurants' in parsed_content:
                                 for r in parsed_content['restaurants']:
                                    if isinstance(r, dict):
                                        name = r.get('name', 'Unknown')
                                        restaurants_map[name] = r
                            if 'hotels' in parsed_content:
                                for h in parsed_content['hotels']:
                                    if isinstance(h, dict):
                                        name = h.get('name', 'Unknown')
                                        hotels_map[name] = h
                            if 'attractions' in parsed_content:
                                for a in parsed_content['attractions']:
                                    if isinstance(a, dict):
                                        name = a.get('name', 'Unknown')
                                        attractions_map[name] = a
                        elif isinstance(parsed_content, list):
                            # Maybe the content IS the list of places?
                            # Check description to see category?
                            desc = item.get('Description', '').lower()
                            category = 'attraction' # default
                            if 'restaurant' in desc: category = 'restaurant'
                            elif 'hotel' in desc: category = 'hotel'
                            
                            for p in parsed_content:
                                if isinstance(p, dict):
                                    name = p.get('name', 'Unknown')
                                    if category == 'restaurant': restaurants_map[name] = p
                                    elif category == 'hotel': hotels_map[name] = p
                                    else: attractions_map[name] = p

            # Fallback: if ref_info items directly contain the keys (already handled by logic below if we didn't continue)
            # But since we handled the list here, we should stick to it.
            continue

        if 'restaurants' in ref_info:
            for r in ref_info['restaurants']:
                if isinstance(r, dict):
                     name = r.get('name', 'Unknown')
                     restaurants_map[name] = r
                     
        if 'hotels' in ref_info:
            for h in ref_info['hotels']:
                if isinstance(h, dict):
                    name = h.get('name', 'Unknown')
                    hotels_map[name] = h

        if 'attractions' in ref_info:
            for a in ref_info['attractions']:
                if isinstance(a, dict):
                    name = a.get('name', 'Unknown')
                    attractions_map[name] = a
        
        count += 1
        if count > 500: # Limit for speed
            break

    print(f"Found {len(restaurants_map)} restaurants, {len(hotels_map)} hotels, {len(attractions_map)} attractions.")

    # 3. Create Documents for Chroma
    docs = []
    
    def create_docs(data_map, category):
        category_docs = []
        for name, info in data_map.items():
            content = f"{category.title()}: {name}\n"
            for k, v in info.items():
                if k != 'name':
                    content += f"{k}: {v}\n"
            
            doc = Document(
                page_content=content,
                metadata={"name": name, "category": category, **{k: str(v) for k, v in info.items() if isinstance(v, (str, int, float, bool))}}
            )
            category_docs.append(doc)
        return category_docs

    docs.extend(create_docs(restaurants_map, "restaurant"))
    docs.extend(create_docs(hotels_map, "hotel"))
    docs.extend(create_docs(attractions_map, "attraction"))
    
    if not docs:
        print("No documents found. Check dataset structure.")
        return

    # 4. Ingest into Chroma
    print(f"Ingesting {len(docs)} documents into ChromaDB at {PERSIST_DIRECTORY}...")
    
    rest_docs = [d for d in docs if d.metadata['category'] == 'restaurant']
    hotel_docs = [d for d in docs if d.metadata['category'] == 'hotel']
    attr_docs = [d for d in docs if d.metadata['category'] == 'attraction']
    
    if rest_docs:
        Chroma.from_documents(documents=rest_docs, embedding=embeddings, collection_name="restaurants", persist_directory=PERSIST_DIRECTORY)
        print(f"Ingested {len(rest_docs)} restaurants.")

    if hotel_docs:
        Chroma.from_documents(documents=hotel_docs, embedding=embeddings, collection_name="hotels", persist_directory=PERSIST_DIRECTORY)
        print(f"Ingested {len(hotel_docs)} hotels.")
        
    if attr_docs:
        Chroma.from_documents(documents=attr_docs, embedding=embeddings, collection_name="attractions", persist_directory=PERSIST_DIRECTORY)
        print(f"Ingested {len(attr_docs)} attractions.")

    print("Data ingestion complete.")

if __name__ == "__main__":
    ingest()
