from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

class GraphState(TypedDict):
    """
    State definition for the storytelling graph.

    Attributes:
        messages: Conversation history between user and AI.
        is_safe: Whether the latest user input passed the guardrail check.
        story_over: Flag indicating if the story has concluded.
        unsafe_attempts: Count of consecutive unsafe inputs.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    is_safe: bool
    story_over: bool
    unsafe_attempts: int  # Counter for consecutive unsafe inputs

class StorySummary(BaseModel):
    """Model for summarizing the story context."""
    summary: str = Field(description="Concise summary of the story so far, including key characters and events.")

class SafetyCheck(BaseModel):
    """Model for safety check results."""
    is_safe: bool = Field(description="True if the input is appropriate for a child, False otherwise.")
    reason: str = Field(description="A brief explanation for the safety classification.")

class StoryContinuation(BaseModel):
    """Model for story continuation responses."""
    narrative: str = Field(description="ONLY the story content - one paragraph (3-4 sentences) with NO questions included.")
    question_to_user: str = Field(description="ONLY one simple, natural question to ask the child - separate from the narrative.")
    story_is_over: bool = Field(description="True if the story has reached a natural conclusion, False otherwise.")

class UserInformation(BaseModel):
    """Model for user information."""
    name: str = Field(description="Name of the user.")
    age: int = Field(description="Age of the user.")
    is_both_fields: bool = Field(description="True if both name and age are provided, False if either is missing.")

# === Application Constants ===
STRIKE_LIMIT = 3  # Number of unsafe attempts allowed before ending session
DB_FILE = "user_stories.db"