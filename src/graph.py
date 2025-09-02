import logging
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain.memory import ConversationBufferMemory

from schema import GraphState, SafetyCheck, StoryContinuation, STRIKE_LIMIT 
from helper import (
    SAFETY_CHECK_PROMPT,
    UNSAFE_INPUT_WARNING,
    TOO_MANY_STRIKES_MESSAGE,
    CONTINUE_CONVERSATION_PROMPT
)

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# === Environment & LLM Setup ===
load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)
guardrail_llm = llm.with_structured_output(SafetyCheck)
storyteller_llm = llm.with_structured_output(StoryContinuation)
memory = ConversationBufferMemory(memory_key="messages", max_token_limit=5000, return_messages=True)

# === Nodes ===
def guardrail_node(state: GraphState):
    user_input = state["messages"][-1].content
    logger.info("Guardrail node triggered with input: %s", user_input)

    try:
        result = guardrail_llm.invoke(SAFETY_CHECK_PROMPT.format(user_input=user_input))
    except Exception as e:
        logger.exception("Guardrail LLM failed")
        return {"is_safe": True, "unsafe_attempts": state.get("unsafe_attempts", 0)}

    logger.info("Guardrail decision: is_safe=%s, reason='%s'", result.is_safe, result.reason)

    current_attempts = state.get("unsafe_attempts", 0)
    
    if result.is_safe:
        memory.chat_memory.add_user_message(user_input)
    return {
        "is_safe": result.is_safe,
        "unsafe_attempts": 0 if result.is_safe else current_attempts + 1
    }


def story_teller_node(state: GraphState):
    logger.info("Storyteller node triggered with %d messages", len(state["messages"]))

    try:
        past_conversation = memory.load_memory_variables({})["messages"]
        print(past_conversation)
        result = storyteller_llm.invoke(
            CONTINUE_CONVERSATION_PROMPT.format(messages=past_conversation)
        )
    except Exception as e:
        logger.exception("Storyteller LLM failed")
        return {"messages": [AIMessage(content="Sorry, I had trouble continuing the story.")], "story_over": False}

    ai_text = f"{result.narrative}\n\n{result.question_to_user}"
    logger.info("AI narrative (truncated): %s", ai_text.replace("\n", " ")[:200])
    memory.chat_memory.add_ai_message(ai_text)
    logger.info(f"Should end: {result.story_is_over}")
    
    return {
        "messages": [AIMessage(content=ai_text)],
        "story_over": result.story_is_over
    }

def handle_unsafe_input_node(state: GraphState):
    """Warn the user when input is unsafe but strike limit not reached."""
    logger.warning("handle_unsafe_input_node: unsafe input detected; sending warning.")
    return {"messages": [AIMessage(content=UNSAFE_INPUT_WARNING)]}


def too_many_strikes_node(state: GraphState):
    """Terminate sessions that exceed the strike limit."""
    logger.warning("too_many_strikes_node: strike limit exceeded; ending session.")
    return {"messages": [AIMessage(content=TOO_MANY_STRIKES_MESSAGE)], "story_over": True}


# === Edges ===
def should_continue(state: GraphState):
    logger.info("should_continue: is_safe=%s unsafe_attempts=%d", state["is_safe"], state["unsafe_attempts"])
    
    if state["is_safe"]:
        return "continue_story"
    elif state["unsafe_attempts"] >= STRIKE_LIMIT:
        return "terminate_session"
    else:
        return "handle_unsafe_input"

# === Graph Compiler ===
def build_graph():
    logger.info("Building LangGraph workflow")
    workflow = StateGraph(GraphState)

    workflow.add_node("guardrail", guardrail_node)
    workflow.add_node("story_teller", story_teller_node)
    workflow.add_node("handle_unsafe_input", handle_unsafe_input_node)
    workflow.add_node("too_many_strikes", too_many_strikes_node)

    workflow.set_entry_point("guardrail")
    workflow.add_conditional_edges("guardrail", should_continue, {
        "continue_story": "story_teller",
        "handle_unsafe_input": "handle_unsafe_input",
        "terminate_session": "too_many_strikes"
    })

    workflow.add_edge("story_teller", END)
    workflow.add_edge("handle_unsafe_input", END)
    workflow.add_edge("too_many_strikes", END)

    logger.info("LangGraph workflow built successfully")
    return workflow.compile()