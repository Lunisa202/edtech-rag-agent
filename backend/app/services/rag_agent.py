import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_experimental.agents import create_pandas_dataframe_agent

load_dotenv()

# Inicialización
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

# 1. RAG para Conocimiento Narrativo (PDFs)
vector_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
retriever = vector_db.as_retriever(search_type="mmr", search_kwargs={"k": 6})

# 2. Agente para Datos Estructurados (CSV)
df = pd.read_csv('data/cursos_escuela.csv')
pandas_agent = create_pandas_dataframe_agent(
    llm, 
    df, 
    verbose=False, 
    allow_dangerous_code=True,
    # ESTA ES LA CLAVE PARA TU ERROR:
    handle_parsing_errors=True,
    # Usamos 'zero-shot-react-description' para que sea más estable
    agent_type="tool-calling", 
    prefix="""Eres el experto en datos de TechAcademy. Responde ÚNICAMENTE en español.
    Analiza el dataframe 'df'. Si te piden filtrar, listar o contar, usa funciones de pandas.
    Explicación: Siempre justifica tu respuesta con los datos de la tabla. 
    Seguridad: Si la respuesta no está en los datos, di que no tienes esa información y no inventes."""
)

# 3. Prompt RAG Reforzado (Para evitar alucinaciones y forzar español)
rag_prompt = PromptTemplate.from_template("""
Eres el asistente oficial de TechAcademy. Responde ÚNICAMENTE en español.
Tu única fuente de verdad es este contexto: {context}.
Si la respuesta no está presente en el contexto, DEBES responder: 'Lo siento, no tengo esa información.'
No intentes completar la respuesta con conocimiento externo.

Contexto: {context}
Pregunta: {input}
Respuesta:
""")

rag_chain = (
    {"context": RunnableLambda(lambda x: "\n\n".join(doc.page_content for doc in retriever.invoke(x["input"]))),
     "input": lambda x: x["input"], "history": lambda x: x["history"]}
    | rag_prompt | llm | StrOutputParser()
)

def answer_question(question: str, message_history: list) -> str:
    q_lower = question.lower()
    
    # Router: Detecta si es una pregunta de datos
    data_keywords = ["lista", "cuantos", "cuales", "precio", "costo", "modalidad", "nivel", "virtual", "presencial"]
    
    if any(word in q_lower for word in data_keywords):
        return pandas_agent.invoke(question)["output"]
    
    # RAG para dudas generales
    hist = "\n".join([f"{msg.sender.upper()}: {msg.text}" for msg in message_history])
    return rag_chain.invoke({"input": question, "history": hist})