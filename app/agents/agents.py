import os
from dotenv import load_dotenv
# 1. Using the modern package
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# 2. Modern ReAct agent constructor
from langgraph.prebuilt import create_react_agent
from app.agents.tool import web_search, scrape_url

load_dotenv()

# --- Model Setup ---
llm_base = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    huggingfacehub_api_token=os.getenv("HUGGING_FACE_API_KEY"), 
    temperature=0.7,
    max_new_tokens=1024, # Increased for the Writer chain
    timeout=300 
)

# 3. CRITICAL: Wrap the LLM to enable tool-calling (bind_tools)
llm = ChatHuggingFace(llm=llm_base)

# --- Agent Builders ---
def build_search_agent():
    # create_react_agent handles the Thought/Action/Observation loop automatically
    return create_react_agent(model=llm, tools=[web_search])

def build_reader_agent():
    return create_react_agent(model=llm, tools=[scrape_url])

# --- Writer Chain ---
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.
Topic: {topic}
Research Gathered:
{research}
Structure the report professionally with Introduction, Key Findings, Conclusion, and Sources."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# --- Critic Chain ---
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Respond with a Score, Strengths, Improvements, and a one-line verdict."),
    ("human", "Report to review:\n{report}"),
])

critic_chain = critic_prompt | llm | StrOutputParser()