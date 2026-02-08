# Copilot Instructions

## Communication
- Think in English and respond in Japanese.  
- Ask the user for clarification when necessary to ensure the request is well-defined.  
- After completing a task, explain what was done and describe possible next steps for the user.  
- Always explain your work to the user and, if appropriate, propose subsequent actions.  
- Before implementing anything, confirm the planned work with the user and obtain their approval.  

## Workflow
- When a task involves multiple steps, divide it into stages and proceed with `git commit` after each.  
  - Use **semantic commit messages**.  

## Development Environment & Tools
- If command output is not visible, use `get last command` or `check background terminal` to verify it.  
- Always use **uv** to run commands.  
  - Prefer `uv run <command>` over `uv run python <command>`.  
- Use **uv** to install any additional libraries.  
- After code generation, format it with **ruff**.  
- Also run `check --fix --select I` to organize import statements.  
- Libraries used only for development should be installed as **dev dependencies**.  

## Coding Guidelines
- Do not use emojis in code.  
- Place all import statements at the top of the file.  
- Add type hints wherever possible.  
- Avoid using runtime arguments in scripts whenever feasible.  
- Since Python 3.12+ is used, apply type hint syntax introduced in 3.12 or later.  
  - Specifically, use built-in `list` and `dict` instead of importing from `typing`.  
- When processing large datasets, organize them by creating separate directories per dataset.  
- Use **pydantic’s BaseModel** to define data structures when appropriate.  
- Display progress when performing loop-based processing.  
- Temporary test scripts should be stored in a `tmp` directory and listed in `.gitignore`.  
- Always use **relative paths** for file references.  
- Use **pathlib** for file operations.  

## Documentation
- All documentation must be written in **Markdown** format.  
- Include a **table of contents** in each document.  
- Store all documents in the **docs** directory.  
