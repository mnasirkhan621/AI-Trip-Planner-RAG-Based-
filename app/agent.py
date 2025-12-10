import os
import json
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from datasets import load_dataset
from dotenv import load_dotenv

from app.models import Itinerary
from app.rag import get_retriever

load_dotenv()

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# 1. Load Few-Shot Examples
# We will cache this to avoid loading dataset on every request
FEW_SHOT_EXAMPLES = ""

def load_few_shot_examples():
    global FEW_SHOT_EXAMPLES
    if FEW_SHOT_EXAMPLES:
        return FEW_SHOT_EXAMPLES
        
    print("Loading few-shot examples from dataset...")
    try:
        dataset = load_dataset("osunlp/TravelPlanner", "validation", split="validation", streaming=True)
        # Take 2 examples
        examples = list(dataset.take(2))
        
        formatted_examples = ""
        for i, ex in enumerate(examples):
            formatted_examples += f"\nExample {i+1}:\n"
            formatted_examples += f"Query: {ex['query']}\n"
            # Format the plan nicely
            # The 'plan' field structure varies, let's dump it as JSON for the model to learn the structure
            formatted_examples += f"Answer: {json.dumps(ex['plan'], indent=2)}\n"
            
        FEW_SHOT_EXAMPLES = formatted_examples
    except Exception as e:
        print(f"Error loading few-shot examples: {e}")
        FEW_SHOT_EXAMPLES = "No examples available."
    
    return FEW_SHOT_EXAMPLES

# 2. Define Prompt
# We expect the retriever to provide relevant context strings
def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

system_template = """You are an expert Travel Agent. Your goal is to plan a detailed itinerary for the user based on their request.

RULES:
1. You MUST use the provided Context to find real hotels, restaurants, and attractions.
2. Do NOT hallucinate places. Only recommend places found in the Context.
3. Follow the schema strictly.
4. If the context doesn't contain enough info, do your best with what is available, but prioritize accuracy.

CONTEXT:
{context}

FEW-SHOT EXAMPLES:
{examples}
"""

user_template = "{query}"

prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("user", user_template)
])

# 3. Create Chain
# structured_llm = llm.with_structured_output(Itinerary) # This is preferred for consistency
# However, standard PydanticOutputParser is also fine if `with_structured_output` isn't fully stable for complex nested reasoning in Flash, 
# but Flash 1.5 is good at it. Let's use with_structured_output.

retriever = get_retriever()

def get_agent_chain():
    # Ensure examples are loaded
    examples = load_few_shot_examples()
    
    chain = (
        {
            "context": RunnableLambda(retriever.invoke) | format_docs,
            "examples": lambda x: examples,
            "query": RunnablePassthrough()
        }
        | prompt
        | llm.with_structured_output(Itinerary)
    )
    return chain

def plan_trip(query: str) -> Itinerary:
    chain = get_agent_chain()
    result = chain.invoke(query)
    return result
