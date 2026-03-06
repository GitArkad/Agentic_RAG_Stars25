# import os
# from dotenv import load_dotenv
# from langchain_groq import ChatGroq
# from langgraph.graph import END
# from src.agent.state import AgentState
# from src.agent.tools import tools

# load_dotenv()

# llm = ChatGroq(
#     model="openai/gpt-oss-120b",
#     temperature=0,
#     GROQ_API_KEY=os.getenv('GROQ_API_KEY')
# )
# llm_with_tools = llm.bind_tools(tools)

# def call_model(state: AgentState):
#     # прямой вызов без проверок
#     return {"messages": [llm_with_tools.invoke(state['messages'])]}

# def should_continue(state: AgentState):
#     last_message = state["messages"][-1]
#     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#         return "tools"
#     return END

# def agent_node(state: State) -> Dict[str, Any]:
#     if state["search_mode"] and state["profile"] and not state["last_search_results"]:
#         vacancies = search_vacancies_tool(state["profile"])
#         return {
#             "last_search_results": vacancies,
#             "search_mode": False
#         }

#     # Если вакансии есть, и пользователь спрашивает про них
#     last_msg = state["messages"][-1].content if state["messages"] else ""
#     if state["last_search_results"] and "ближе к моему" in last_msg.lower():
#         analysis = match_analyzer_tool(state["profile"], state["last_search_results"][0])
#         return {
#             "last_search_results": [analysis]
#         }

#     # Ответ через LLM (Groq)
#     response = llm.invoke([msg for msg in state["messages"]])  # или форматировать по-своему
#     return {
#         "messages": [response]
#     }

# def context_manager_node(state: State) -> Dict[str, Any]:
#     last_msg = state["messages"][-1].content if state["messages"] else ""

#     if "резюме" in last_msg.lower() and not state["resume_processed"]:
#         profile = parse_resume_tool(last_msg)
#         return {
#             "profile": profile,
#             "resume_processed": True,
#             "search_mode": True
#         }

#     if "найди" in last_msg.lower() and state["profile"]:
#         return {"search_mode": True}

#     return {}