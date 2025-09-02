"""
Pydantic models for the storytelling assistant.
"""

import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from schema import STRIKE_LIMIT, StorySummary
from database import db 
from helper import SUMMARY_PROMPT, INITIAL_CONVERSATION_PROMPT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)
summary_llm = llm.with_structured_output(StorySummary) # for summarizing the story context after a session

def summarize_conversation(messages):
    text_history = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
        for m in messages
    )
    try:
        summary = llm.invoke(SUMMARY_PROMPT.format(messages=text_history)).content
        return summary
    except Exception as e:
        logger.exception("Failed to summarize conversation: %s", e)
        return None


class SessionManager:
    def __init__(self, session_id: str, workflow_app, memory):
        self.session_id = session_id
        self.workflow_app = workflow_app
        
        # Initialize state
        self.current_state = {
            "messages": None,
            "unsafe_attempts": 0,
            "is_safe": True,
            "story_over": False,
            "awaiting_user_info": False,
        }
        self.memory = memory
        
        self.message_count = 1
        self.summary = None
        self.number = 0
        self.greeted = False
        self.started_conversation = False
        
        # user profile info
        self.parental_guidelines = ""
        
    def reset(self):
        """Reset the session to initial state."""
        self.current_state = {
            "messages": None,
            "unsafe_attempts": 0,
            "is_safe": True,
            "story_over": False,
            "awaiting_user_info": False,
        }
        self.memory.clear()
        self.message_count = 1
        self.summary = None
        self.number = 0
        self.greeted = False
        self.started_conversation = False

    def process_user_input(self, user_input: str) -> str:
        logger.info(f"Session {self.session_id} - Processing user input #{self.message_count}: '{user_input}'")
        logger.info("No messages" if self.current_state["messages"] is None else f"  Total messages: {len(self.current_state['messages'])}")
        logger.info(f"  Is safe: {self.current_state.get('is_safe', True)}")
        logger.info(f"  Is over: {self.current_state.get('story_over', True)}")
        logger.info(f"  Last user message: '{user_input}'")
        
        # first interaction, load previous story if exists and add system prompt
        if self.current_state["messages"] is None:
            self.summary = self.get_user_story()
            if self.summary:
                logger.info(f"Loaded story summary: '{self.summary}'")
                # add parental guidelines and possible interests
                first_content = INITIAL_CONVERSATION_PROMPT.format(memory_summary=self.summary)
            else:
                logger.info("No existing story found for user that are not completed.")
                first_content = INITIAL_CONVERSATION_PROMPT.format(memory_summary="No prior story.")
            
            system_content = SYSTEM_PROMPT.format(parental_guidelines=self.parental_guidelines)
            system_prompt_message = SystemMessage(content=system_content)
            
            self.current_state["messages"] = [system_prompt_message]
            self.current_state["messages"].append(AIMessage(content=first_content))
            self.memory.chat_memory.add_message(system_prompt_message)
            self.memory.chat_memory.add_message(AIMessage(content=first_content))
            self.message_count += 2
        
        #TODO: enable starting a new story if the previous one ended
        if self.current_state.get("story_over", False):
            return "The story has ended. Please start a new session."

        self.current_state["messages"].append(HumanMessage(content=user_input))
        self.message_count += 1

        # Run the graph workflow
        try:
            for event in self.workflow_app.stream(self.current_state, config={"recursion_limit": 100}, stream_mode="values"):
                self.current_state.update(event)
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return "Sorry, something went wrong processing your input."

        # Get latest AI message
        newest_ai_message = self.current_state["messages"][-1]
        if isinstance(newest_ai_message, AIMessage):
            self.message_count += 1
        
        logger.info(f"Iznad ispitivanja: {self.current_state['story_over']}")
        # Close session if story ended, but if it was unsafe, save the story as "suspended" so it can continue later
        if self.current_state["story_over"]:
            logger.info(f"Session {self.session_id} - Story ended.")
            db.save_story(self.session_id, summarize_conversation(self.current_state["messages"]), "completed")
            logger.info(f"Session {self.session_id} - Story saved as completed.")
            
        if self.current_state.get("unsafe_attempts", 0) >= STRIKE_LIMIT:
            logger.info(f"Session {self.session_id} - Story suspended due to unsafe content.")
            db.save_story(self.session_id, summarize_conversation(self.current_state["messages"]), "suspended")
            logger.info(f"Session {self.session_id} - Story saved as suspended.")
            
        return newest_ai_message.content
    
    def user_exists(self):
        """Check if the user exists in the database."""
        return db.get_user(self.session_id)
    
    def create_user(self, name, age):
        """Create a new user in the database."""
        db.create_user(self.session_id, name, age)
        return db.get_user(self.session_id)
    
    def get_user_story(self):
        """Retrieve the user's current story."""
        return db.get_story(self.session_id)