from backend.agents.crew_lite import Agent, Task, Crew, Process
from backend.agents.config import get_llm
from backend.agents.tools import AgentTools

llm = get_llm()

# --- Define Advanced Agents ---

lead_dev = Agent(
    role='Lead Next.js Developer',
    goal='Write production-grade Next.js 14 code with TypeScript and TailwindCSS.',
    backstory='You are a 10x developer. You write clean, accessible, and performant code. You adhere strictly to the "use client" directive where necessary.',
    llm=llm,
    tools=[AgentTools.write_file, AgentTools.read_file]
)

security_analyst = Agent(
    role='Application Security Analyst',
    goal='Review code for vulnerabilities (XSS, Injection, Auth) and Approve/Reject it.',
    backstory='You are a gatekeeper. You NEVER let insecure code pass. You check for missing validation, secrets in code, and dangerous patterns. You output "APPROVE" only if it is safe.',
    llm=llm,
    tools=[AgentTools.read_file]
)

tech_writer = Agent(
    role='Technical Writer',
    goal='Write comprehensive documentation and JSDoc comments.',
    backstory='You turn complex code into easy-to-understand documentation. You update READMEs and add JSDocs.',
    llm=llm,
    tools=[AgentTools.write_file, AgentTools.read_file]
)

def run_feature_workflow(feature_description: str):
    context = ""
    
    # Step 1: Development
    print(f"Lead Dev working on: {feature_description}")
    dev_task = f"Create a Next.js component for: {feature_description}. Save it to 'components/agents/generated/Feature.tsx'."
    code_output = lead_dev.execute(dev_task, context)
    context += f"\n\n[Lead Dev]: {code_output}"
    
    # Step 2: Security Review Loop (Max 1 retry for this demo)
    max_retries = 1
    approved = False
    
    for i in range(max_retries + 1):
        print(f"Security Review (Attempt {i+1})...")
        sec_task = "Review 'components/agents/generated/Feature.tsx'. If safe, output 'APPROVE'. If unsafe, output 'REJECT' and explain why."
        sec_output = security_analyst.execute(sec_task, context)
        context += f"\n\n[Security]: {sec_output}"
        
        if "APPROVE" in sec_output.upper():
            approved = True
            print("Security Approved.")
            break
        else:
            print("Security Rejected. Sending back to Dev...")
            fix_task = f"Fix the security issues identified: {sec_output}. Update 'components/agents/generated/Feature.tsx'."
            fix_output = lead_dev.execute(fix_task, context)
            context += f"\n\n[Lead Dev - Fix]: {fix_output}"
    
    if not approved:
        return "Workflow Failed: Security did not approve the code."

    # Step 3: Documentation
    print("Generating Documentation...")
    doc_task = "Read 'components/agents/generated/Feature.tsx' and write JSDoc comments for it. Also create 'components/agents/generated/README.md'."
    doc_output = tech_writer.execute(doc_task, context)
    context += f"\n\n[Tech Writer]: {doc_output}"
    
    return "Workflow Complete. Code Approved and Documented."
