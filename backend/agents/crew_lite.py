from typing import List, Any
from pydantic import BaseModel
from langchain.chat_models.base import BaseChatModel
from langchain.schema import HumanMessage, SystemMessage

class Agent(BaseModel):
    role: str
    goal: str
    backstory: str
    tools: List[Any] = []
    llm: Any
    verbose: bool = False

    class Config:
        arbitrary_types_allowed = True

    def execute(self, task_description: str, context: str = "") -> str:
        prompt = f"""
You are a {self.role}.
Goal: {self.goal}
Backstory: {self.backstory}

Your Task: {task_description}

Context from previous steps:
{context}

You have access to tools, but for this interaction, please output the final result directly.
If you need to use a tool, describe the action you would take, but primarily focus on generating the content requested (Code, Test, or Report).
"""
        messages = [
            SystemMessage(content=self.backstory),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content

class Task(BaseModel):
    description: str
    agent: Agent
    expected_output: str

class Crew(BaseModel):
    agents: List[Agent]
    tasks: List[Task]
    verbose: int = 0

    def kickoff(self):
        context = ""
        results = []
        
        for i, task in enumerate(self.tasks):
            print(f"Starting Task {i+1}: {task.description}")
            result = task.agent.execute(task.description, context)
            results.append(result)
            context += f"\n\nOutput from {task.agent.role}:\n{result}"
            print(f"Task {i+1} Complete.")
            
        return "Workflow Completed Successfully.\n" + context

class Process:
    sequential = "sequential"
