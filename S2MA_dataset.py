import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel
from tqdm import tqdm
from typing import List

# CSV paths
input_csv = "NormaV1.csv"
output_csv = "NormaV2.csv"
local_llm = "qwen2.5:latest"

# Define structured response model
class AgentResponseList(BaseModel):
    agent1: str
    agent2: str
    agent3: str

# Load model
llm = ChatOllama(model=local_llm, temperature=0.2)

# Main LLM invocation function with structured output
def generate_agent_outputs(llm, question, answer):
    system_msg = SystemMessage(content=(
        """You're an expert in Moroccan customs nomenclature automation. Your task is to simulate multi-agent step-by-step reasoning given a question and answer.\n\n

        Your goal is to generate 3 intermediate outputs. Each output corresponds to one of the following agents: HScodeFinder, ProductIdentifier, ChapterClassifier.\n\n
        Select the most logical agent order based on the question type in order to arrive to the answer:\n
        
        - 1. ProductIdentifier → ChapterClassifier → HScodeFinder: when the question gives a product name and asks for the HS code.\n
        - 2. HScodeFinder → ProductIdentifier → ChapterClassifier: when the question gives an HS code and asks about its classification.\n
        - 3. HScodeFinder → ChapterClassifier → ProductIdentifier: when the question gives an HS code and asks 
        
        for the chemical name, always mention the agent name in the beginning of each response like this: (AgentName) reasoning...\n\n
        
        Few-shot example:\n
        Question: What does the HS code HS:2901100000 specifically refer to in terms of chemical compounds?\n
        Answer: code HS:2901100000 refers to Saturates, which may or may not be part of Hydrocarbons acyclic.\n\n
        
        Expected response format:
        {
        "agent1": "(HScodeFinder) ...",
        "agent2": "(ChapterClassifier) ...",
        "agent3": "(ProductIdentifier) ..."
        }"""
    ))

    prompt = f"Question: {question}\nAnswer: {answer}"

    # Get structured output
    structured_llm = llm.with_structured_output(AgentResponseList)
    response: AgentResponseList = structured_llm.invoke([system_msg, HumanMessage(content=prompt)])

    return [response.agent1, response.agent2, response.agent3]

# Process the dataset
df = pd.read_csv(input_csv)
output_rows = []

print("🚀 Generating multi-agent dataset...")

# Limit to 3 rows for debugging
for _, row in tqdm(df.head(3).iterrows(), total=3):
    question = str(row['question'])
    answer = str(row['answer'])
    print(f"\n🔍 Processing Question: {question[:80]}")

    try:
        agent_outputs = generate_agent_outputs(llm, question, answer)
        if len(agent_outputs) == 3:
            output_rows.append([question] + agent_outputs + [answer])
        else:
            print(f"⚠️ Skipped row due to malformed output: {question}")
    except Exception as e:
        print(f"❌ Error on question: {question[:80]}... → {e}")

# Save results
final_df = pd.DataFrame(output_rows, columns=[
    "question", "agent1", "agent2", "agent3", "final_answer"
])
final_df.to_csv(output_csv, index=False)
print(f"✅ Reformatted dataset saved to: {output_csv}")
