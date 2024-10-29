import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tiktoken
# estimate token cost

def estimate_token_cost(text, model:str):
    cost_reference = {"gpt-4o-mini": 10/1000000,
                      "gpt-4o": 30/1000000,
                      'gpt-4o-2024-08-06': 30/1000000,
                      "gpt-3.5-turbo": 15/1000000,
                      "text-embedding-3-large": 1/1000000,
                      "text-embedding-3-small": 0.5/1000000,
                      "text-embedding-3-base": 1/1000000,
                      "text-embedding-3-mini": 0.5/1000000}
    encoding = tiktoken.encoding_for_model(model)
    tokens = len(encoding.encode(text))
    usd = tokens * cost_reference[model]
    return usd

# Example usage
print(estimate_token_cost("Hello, world!", "gpt-4o-mini"))

definitions = {
    "CognitiveTask": "A cognitive task is a specific activity or test designed to measure or elicit a particular cognitive process or concept. A cognitive task is performed during fMRI scanning.",
}
system_prompts = {
    # Extract Cognitive Task from Methods Section
    "CognitiveTask":'''
You are an expert in cognitive neuroscience. You are provided with text sample of a scientific paper.
You should extract the relevant terms from the text that best describe the cognitive task.
'''+definitions['CognitiveTask']+'''
You should return a JSON formatted list of terms that describe the cognitive tasks performed during fMRI scanning.
If you do not know the value of an attribute asked to extract, return null for the attribute's value.
If you do not know if an attribute is present, return null for the attribute's value.
This is very important to my career.

#### JSON output format ####
{"cognitive_task": [<str>,<str>,...]}

#### Example null output ####
{"cognitive_task": [null]}
''',
# Extract Cognitive Task Descriptions from Methods Section
    "CognitiveTaskDescription":'''
You are an expert in cognitive neuroscience. You are provided with a list of the methods section of scientific paper abstracts.
You should return a list of the original text that best describe the cognitive task(s) performed during fMRI scanning.
'''+definitions['CognitiveTask']+'''If you do not know the value of an attribute asked to extract, return null for the attribute's value.
If you do not know if an attribute is present, return null for the attribute's value.
This is very important to my career.

#### JSON output format ####
{"cognitive_task_description": [<str>,<str>,...]}

#### Example null output ####
{cognitive_task_description": [null]}
'''
}