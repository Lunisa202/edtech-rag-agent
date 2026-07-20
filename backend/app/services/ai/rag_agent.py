import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List
from langchain_experimental.agents import create_pandas_dataframe_agent

# --- 1. CONFIGURATION ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

# Load data once at the module level (Global scope)
df = pd.read_csv('data/cursos_escuela.csv')
vector_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
retriever = vector_db.as_retriever(search_type="mmr", search_kwargs={"k": 5})

# --- 2. MEMORY LOGIC  ---
def truncate_history(history: List[dict], max_chars: int = 300) -> List:
    formatted_messages = []
    # Process the last 6 messages to keep context short
    for msg in history[-6:]:
        content = msg.get("content", "")
        if len(content) > max_chars:
            content = "[...] " + content[-max_chars:]
        
        if msg["role"] == "user":
            formatted_messages.append(HumanMessage(content=content))
        else:
            formatted_messages.append(AIMessage(content=content))
    return formatted_messages

# --- 3. STATE AND GRAPH NODES ---
class AgentState(TypedDict):
    question: str
    history: List
    decision: str
    answer: str

def triaging_node(state: AgentState):
    prompt = f"""Analiza la siguiente pregunta del usuario: '{state['question']}'
    
    Tienes dos herramientas disponibles:
    1. 'PANDAS': Úsala ÚNICAMENTE si la pregunta requiere listar cursos, filtrar por precios, horarios, profesores o datos estructurados exactos que están en una tabla numérica/CSV.
    2. 'RAG': Úsala para cualquier otra consulta, incluyendo:
       - Requisitos de inscripción, prerrequisitos de cursos o documentos necesarios.
       - Modalidades de estudio (virtual, presencial, semipresencial), sedes o asistencias.
       - Políticas financieras, reembolsos, becas o congelamiento de vacantes.
       - Reglamento, notas, promedios, plazos de certificados o soporte técnico del EVA.

    Responde ÚNICAMENTE con una de estas dos palabras, sin explicaciones: 'PANDAS' o 'RAG'."""
    
    decision = llm.invoke(prompt).content.strip().upper()
    if "PANDAS" in decision:
        decision = "PANDAS"
    else:
        decision = "RAG"
        
    return {"decision": decision}

def pandas_node(state: AgentState):
    agent = create_pandas_dataframe_agent(llm, df, allow_dangerous_code=True, verbose=False)
    output = agent.invoke(state['question'])["output"]
    return {"answer": output}

def rag_node(state: AgentState):
    docs = retriever.invoke(state['question'])
    context = "\n\n".join([d.page_content for d in docs])
    
    prompt = f"""Eres el asistente oficial de TechAcademy. Responde a la pregunta del usuario basándote estrictamente en el siguiente contexto recuperado de la documentación oficial. Si la información no está en el contexto, indícalo amablemente.

    Contexto:
    {context}

    Pregunta del usuario: {state['question']}"""
    
    response = llm.invoke(prompt).content
    return {"answer": response}

# --- 4. GRAPH CONSTRUCTION ---
workflow = StateGraph(AgentState)
workflow.add_node("triaging", triaging_node)
workflow.add_node("pandas", pandas_node)
workflow.add_node("rag", rag_node)

workflow.add_edge(START, "triaging")
workflow.add_conditional_edges("triaging", lambda x: x["decision"], {"RAG": "rag", "PANDAS": "pandas"})
workflow.add_edge("pandas", END)
workflow.add_edge("rag", END)

app = workflow.compile()

# --- 5. EXPOSED FUNCTION ---
def answer_question(question: str, history: list):
    # Convert DB objects to expected dict format
    formatted_history = []
    for msg in history:
        role = "user" if msg.sender == "user" else "assistant"
        formatted_history.append({"role": role, "content": msg.text})
    
    truncated_history = truncate_history(formatted_history)
    result = app.invoke({"question": question, "history": truncated_history})
    return result["answer"]