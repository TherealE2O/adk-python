"""AI agents for the novel editor."""

from .base import BaseAgent, WorldBuildingAgentInterface, EditingAgentInterface
from .worldbuilding_agent import WorldBuildingAgent
from .editing_agent import EditingAgent

__all__ = [
    'BaseAgent',
    'WorldBuildingAgentInterface',
    'EditingAgentInterface',
    'WorldBuildingAgent', 
    'EditingAgent'
]
