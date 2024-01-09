"""
Settings module for GPT Engineer project.

This module contains the Settings class which encapsulates all the application settings.
"""

from dataclasses import dataclass

@dataclass
class Settings:
    """
    A dataclass to store all settings for the GPT Engineer application.
    """
    project_path: str
    model: str
    temperature: float
    steps_config: str
    improve_mode: bool
    lite_mode: bool
    azure_endpoint: str
    chat_mode: bool
    use_git: bool
    role: str
    prompt_file: str
    verbose: bool
    prompt: str
    file_selector: bool
    build_knowledge: bool