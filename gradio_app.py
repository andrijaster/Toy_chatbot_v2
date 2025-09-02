"""
Gradio web interface for the interactive storytelling assistant.
"""

import gradio as gr
from typing import List, Tuple
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Import from our modules
from src.storytelling.helper import (
    INITIAL_STORY_CONTENT,
    WELCOME_MESSAGE,
    INSTRUCTIONS_MESSAGE,
)
from src.storytelling.database import db
from src.storytelling.core import app


class StorytellingSession:
    """Manages a storytelling session for the Gradio interface."""
    
    def __init__(self):
        self.session_id = None
        self.current_state = None
        self.message_count = 0
        self.reset_session()
    
    def reset_session(self):
        """Resets the session to start a new story."""
        if self.session_id:
            db.close_session(self.session_id, "reset")
        
        self.session_id = db.create_session()
        self.current_state = {
            "messages": [AIMessage(content=INITIAL_STORY_CONTENT)],
            "unsafe_attempts": 0,
            "is_safe": True,
            "story_over": False
        }
        self.message_count = 1
        
        # Save initial message to database
        db.save_message(self.session_id, self.current_state["messages"][0], 0)
        
        return self.format_chat_history()
    
    def process_user_input(self, user_input: str, chat_history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
        """Processes user input and returns updated chat history."""
        if not user_input.strip():
            return chat_history, ""
        
        if self.current_state.get("story_over", False):
            return chat_history + [("Story has ended. Please start a new story.", "")], ""
        
        # Add user message
        user_message = HumanMessage(content=user_input)
        self.current_state["messages"].append(user_message)
        db.save_message(self.session_id, user_message, self.message_count)
        self.message_count += 1
        
        # Process through the graph - pass the COMPLETE conversation history
        try:
            for event in app.stream(self.current_state, config={"recursion_limit": 100}, stream_mode="values"):
                self.current_state.update(event)
            
            # Get the AI response
            newest_ai_message = self.current_state["messages"][-1]
            if isinstance(newest_ai_message, AIMessage):
                # Save AI response to database
                db.save_message(self.session_id, newest_ai_message, self.message_count)
                self.message_count += 1
                
                # Update chat history
                updated_history = chat_history + [(user_input, newest_ai_message.content)]
                
                # Check if story is over
                if self.current_state.get("story_over", False):
                    if self.current_state.get("unsafe_attempts", 0) >= 3:
                        db.close_session(self.session_id, "terminated_unsafe")
                    else:
                        db.close_session(self.session_id, "completed")
                
                return updated_history, ""
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            return chat_history + [(user_input, error_msg)], ""
        
        return chat_history, ""
    
    def format_chat_history(self) -> List[Tuple[str, str]]:
        """Formats the current messages as chat history for Gradio."""
        history = []
        messages = self.current_state["messages"]
        
        # Start with the initial AI message
        if messages and isinstance(messages[0], AIMessage):
            history.append((None, messages[0].content))
        
        # Add pairs of user and AI messages
        for i in range(1, len(messages), 2):
            if i < len(messages):
                user_msg = messages[i].content if isinstance(messages[i], HumanMessage) else ""
                ai_msg = messages[i + 1].content if i + 1 < len(messages) and isinstance(messages[i + 1], AIMessage) else ""
                if user_msg or ai_msg:
                    history.append((user_msg, ai_msg))
        
        return history


# Global session instance
session = StorytellingSession()


def chat_interface(user_input: str, chat_history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
    """Main chat interface function for Gradio."""
    return session.process_user_input(user_input, chat_history)


def reset_story() -> Tuple[List[Tuple[str, str]], str]:
    """Resets the story to start fresh."""
    return session.reset_session(), ""


def get_session_info() -> str:
    """Returns current session information."""
    if session.session_id:
        stats = db.get_session_stats(session.session_id)
        if stats:
            return f"Session ID: {session.session_id}\nMessages: {stats['total_messages']}\nStatus: {stats['status']}"
    return "No active session"


# Create the Gradio interface
def create_interface():
    """Creates and returns the Gradio interface."""
    
    with gr.Blocks(
        title="Interactive Storytelling Assistant",
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 800px; margin: auto; }
        .header { text-align: center; margin-bottom: 20px; }
        .chat-container { height: 500px; }
        """
    ) as interface:
        
        gr.Markdown(
            f"""
            # {WELCOME_MESSAGE}
            
            {INSTRUCTIONS_MESSAGE}
            
            This is an interactive storytelling assistant designed for children aged 6-9.
            The AI will ask you what kind of story you'd like to create, then guide you through a magical, educational adventure where you help shape the narrative.
            
            **Educational Features:**
            - Stories teach valuable lessons about friendship, problem-solving, and kindness
            - Natural learning opportunities woven into exciting adventures
            - Vocabulary building and critical thinking development
            
            **Safety Features:**
            - Content is automatically checked for child-appropriate themes
            - Stories focus on positive, imaginative adventures
            - Inappropriate content is gently redirected
            """,
            elem_classes=["header"]
        )
        
        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(
                    value=session.format_chat_history(),
                    height=500,
                    show_label=False,
                    elem_classes=["chat-container"]
                )
                
                with gr.Row():
                    user_input = gr.Textbox(
                        placeholder="Type your story idea here...",
                        show_label=False,
                        scale=4
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Row():
                    reset_btn = gr.Button("Start New Story", variant="secondary")
                    clear_btn = gr.Button("Clear Chat", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### Session Info")
                session_info = gr.Textbox(
                    value=get_session_info(),
                    label="Current Session",
                    interactive=False,
                    lines=4
                )
                
                refresh_info_btn = gr.Button("Refresh Info", size="sm")
        
        # Event handlers
        submit_btn.click(
            chat_interface,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input]
        )
        
        user_input.submit(
            chat_interface,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input]
        )
        
        reset_btn.click(
            reset_story,
            outputs=[chatbot, user_input]
        )
        
        clear_btn.click(
            lambda: ([], ""),
            outputs=[chatbot, user_input]
        )
        
        refresh_info_btn.click(
            get_session_info,
            outputs=[session_info]
        )
    
    return interface


def main():
    """Launches the Gradio interface."""
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()