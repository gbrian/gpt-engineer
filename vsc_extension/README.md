# GPT-ENGINEER Visual Studio Code Extension

This extension integrates GPT-ENGINEER with Visual Studio Code, allowing for enhanced coding assistance and automation within your editor.

## Features

- **Code Changes Tab**: View and apply suggested code changes directly in VS Code.
- **Task Section**: Write tasks with autocomplete and IntelliSense support.
- **Context Selection**: Choose relevant files and knowledge to inform the task processing.
- **Actions**: Run tasks, improve task definitions, and reset the environment with ease.

## Installation

To install the extension, follow the standard Visual Studio Code extension installation process.

## Usage

After installation, you can access the extension's features through the Command Palette or the dedicated GPT-ENGINEER sidebar.

## Webview Features

- **Single Tab**: Ensures only one webview tab is open at a time.
- **Vue.js Integration**: Displays a Vue.js application within the webview for enhanced user interaction.

## Commands

- `Run Task`: Opens a webview to execute the current task and generate code changes.
- `Improve Task`: Opens a webview to refine the task definition and context selection.
- `New Task`: Opens a webview to clear all inputs and start a new task.

For more information, please refer to the detailed documentation provided within the extension.

## Installation
Explain standar installation process

## Functionalities
This extension allows you to interact with your project

### Code changes tab
This tab let's you create tasks. It has this sections:

#### Task section
This section on the top allows you to write a task, the extension will use intellisense and other VSC services to help 
you autocomplete your task and help whiting.

#### Context
Contex allows you to select pieces of knowledge and files that
will help gpt-engineer to understand and pollish the task

#### Code changes
Like the git extension will show the suggested changes created by
gpt-engineer to allow user validate and apply to existing code

#### Actions sections
 * Run: Executes the task and creates the code changes
 * Improve: Improves task definition and selects the most relevant context
 * New: Resets all values

 