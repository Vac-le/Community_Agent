from pathlib import Path

content = '''from __future__ import annotations

import threading

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from agent.graph.agents import create_knowledge_agent, create_order_agent, create_report_agent, create_weather_agent
from agent.graph.state import AgentState
from agent.graph.supervisor import supervisor_route
from agent.graph.worker import run_worker
from agent.reflection_service import ReflectionService
from memory.user_long_memory_service import UserLongMemoryService
from models.dto import ChatHistoryMessage
from models.factory import chat_model
from utils.logger_handler import logger

ROUTE_TO_NODE={"knowledge":"knowledge_worker","order":"order_worker","report":"report_worker","weather":"weather_worker"}

class MultiAgentExecutor:
    def __init__(self):
        self.knowledge_agent=create_knowledge_agent();self.order_agent=create_order_agent();self.report_agent=create_report_agent();self.weather_agent=create_weather_agent();self.reflection_service=ReflectionService(chat_model);self.user_memory_service=UserLongMemoryService();self.graph=self._build_graph().compile()

    def execute_stream(self,query:str,token:str|None=None,session_id:str|None=None,chat_history:list[ChatHistoryMessage]|None=None,user_id:int|None=None,community_id:int|None=None):
        logger.info(f"[MultiAgent] query={query[:200]}")
        user_memory_context=self.user_memory_service.build_memory_context(user_id,community_id)
        base_messages=self._build_base_messages(query,chat_history,user_memory_context)
        state:AgentState={"query":query,"original_query":query,"token":token,"session_id":session_id,"chat_history":chat_history,"user_id":user_id,"community_id":community_id,"user_memory_context":user_memory_context,"routes":[],"current_route_index":0,"current_route":"","current_worker":"","messages":base_messages,"route_messages":base_messages,"route_answers":[],"called_tools":[],"tool_observations":[],"chart_outputs":[],"control_outputs":[],"food_order_card":None,"final_answer":"","reflection_attempt":0,"should_retry":False,"done":False}
        emitted_chart_urls:set[str]=set();emitted_control_keys:set[str]=set();confirmed_answer=""
        for chunk in self.graph.stream(state,stream_mode="updates"):
            for node_name,node_state in chunk.items():
                for chart in (node_state.get("chart_outputs") or []):
                    url=(chart.get("content") or {}).get("imageUrl","")
                    if url and url not in emitted_chart_urls: emitted_chart_urls.add(url); yield chart
                for ctrl in (node_state.get("control_outputs") or []):
                    key=str(ctrl)
                    if key not in emitted_control_keys: emitted_control_keys.add(key); yield ctrl
                if node_name=="reflector":
                    if node_state.get("should_retry",False):
                        yield {"type":"status","stage":"reflecting","message":"发现结果需要修正，正在根据反思意见重新执行"}
                    else: confirmed_answer=node_state.get("final_answer") or confirmed_answer
                if node_name=="memory_updater":
                    final_answer=node_state.get("final_answer") or confirmed_answer
                    self._async_update_memory(user_id,community_id,query,final_answer)
                    if final_answer: yield final_answer

    def _build_graph(self):
        graph=StateGraph(AgentState)
        graph.add_node("supervisor",self._supervisor_node);graph.add_node("knowledge_worker",self._knowledge_worker_node);graph.add_node("order_worker",self._order_worker_node);graph.add_node("report_worker",self._report_worker_node);graph.add_node("weather_worker",self._weather_worker_node);graph.add_node("final_summarizer",self._final_summarizer_node);graph.add_node("reflector",self._reflector_node);graph.add_node("memory_updater",self._memory_updater_node)
        graph.set_entry_point("supervisor")
        graph.add_conditional_edges("supervisor",self._next_worker_from_state,{"knowledge_worker":"knowledge_worker","order_worker":"order_worker","report_worker":"report_worker","weather_worker":"weather_worker","final_summarizer":"final_summarizer","reflector":"reflector"})
        for worker_node in ROUTE_TO_NODE.values(): graph.add_conditional_edges(worker_node,self._after_worker_decision,{"knowledge_worker":"knowledge_worker","order_worker":"order_worker","report_worker":"report_worker","weather_worker":"weather_worker","final_summarizer":"final_summarizer","reflector":"reflector"})
        graph.add_edge("final_summarizer","reflector");graph.add_conditional_edges("reflector",self._after_reflector_decision,{"supervisor":"supervisor","memory_updater":"memory_updater"});graph.add_edge("memory_updater",END);return graph

    def _supervisor_node(self,state:AgentState)->AgentState:
        routing_query=state.get("query") or state.get("original_query") or "";history_summary=self._build_history_hint(state.get("chat_history"));routes=supervisor_route(routing_query,history_summary)
        retry_instruction="";current_query=state.get("query","");original_query=state.get("original_query") or routing_query
        if state.get("reflection_attempt",0)>0 and current_query and current_query!=original_query: retry_instruction=current_query
        base_messages=self._build_base_messages(routing_query,state.get("chat_history"),state.get("user_memory_context",""))
        if retry_instruction: base_messages.insert(1 if base_messages and base_messages[0]["role"]=="system" else 0,{"role":"system","content":retry_instruction})
        state["routes"]=routes;state["current_route_index"]=0;state["current_route"]=routes[0] if routes else "";state["current_worker"]=ROUTE_TO_NODE.get(state["current_route"],"");state["messages"]=base_messages;state["route_messages"]=base_messages;state["route_answers"]=[];state["final_answer"]="";logger.info(f"[Supervisor] routes={routes} retry_attempt={state.get('reflection_attempt',0)}");return state

    def _knowledge_worker_node(self,state:AgentState)->AgentState:
        state["current_route"]="knowledge";state["current_worker"]="knowledge_worker";return self._advance_route_index(run_worker(self.knowledge_agent,state,"knowledge_agent"))

    def _order_worker_node(self,state:AgentState)->AgentState:
        state["current_route"]="order";state["current_worker"]="order_worker";return self._advance_route_index(run_worker(self.order_agent,state,"order_agent"))

    def _report_worker_node(self,state:AgentState)->AgentState:
        state["current_route"]="report";state["current_worker"]="report_worker";return self._advance_route_index(run_worker(self.report_agent,state,"report_agent"))

    def _weather_worker_node(self,state:AgentState)->AgentState:
        state["current_route"]="weather";state["current_worker"]="weather_worker";return self._advance_route_index(run_worker(self.weather_agent,state,"weather_agent"))
'''

Path(r'c:\Users\一叶知秋\Desktop\新社区项目\Community_Agent\agent\graph\executor.py').write_text(content, encoding='utf-8')
