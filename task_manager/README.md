Python Task Manager

A simple command-line task management application built with Python showcasing functions, modules, object-oriented programming (OOP), type hints, exception handling, testing, and code quality tools.

The project emphasizes clean code, separation of concerns, reusable components, and maintainable project structure.

Table of Contents

- "Overview" (#overview)
- "Features" (#features)
- "Technologies" (#technologies)
- "Project Structure" (#project-structure)
- "Requirements" (#requirements)
- "Installation" (#installation)
- "Usage" (#usage)
- "Example Output" (#example-output)
- "Architecture" (#architecture)
- "Error Handling" (#error-handling)
- "Testing" (#testing)
- "Code Quality" (#code-quality)
- "Learning Objectives" (#learning-objectives)

Overview

The Python Task Manager allows users to create tasks, view their tasks, and mark tasks as completed through a command-line interface.

The application is organized into separate modules, each with a specific responsibility. This makes the code easier to understand, test, maintain, and extend.

Tasks are stored in memory, meaning they are lost when the application terminates.

This project is intended as a learning exercise rather than a production-ready task management system.

Features

- Create tasks with unique IDs.
- View all tasks.
- Mark tasks as completed.
- Track task status using enumerations.
- Validate task titles.
- Handle missing tasks with custom exceptions.
- Separate business logic from user interaction.
- Use type hints to improve readability.
- Test core functionality with pytest.
- Check code quality and formatting with Ruff.

Technologies

Technology| Purpose
Python 3.11+| Core programming language
Dataclasses| Simplify data model creation
Type hints| Make expected types explicit
Enums| Represent task statuses
Pytest| Automated testing
Ruff| Linting and formatting
Git| Version control (optional)

Project Structure

task_manager/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── services.py
│   ├── storage.py
│   └── errors.py
│
├── tests/
│   ├── __init__.py
│   └── test_services.py
│
├── pyproject.toml
└── README.md

Module Responsibilities

"app/main.py"

- Provides the command-line interface.
- Accepts user input.
- Displays task information.
- Handles user-facing errors.

"app/models.py"

- Defines the "Task" dataclass.
- Defines the "TaskStatus" enumeration.
- Contains task-related behavior.

"app/services.py"

- Implements the application's business logic.
- Creates and completes tasks.
- Validates task titles.
- Coordinates task operations with storage.

"app/storage.py"

- Stores tasks in memory.
- Retrieves tasks by ID.
- Returns a copy of the task collection when listing tasks.

"app/errors.py"

- Defines custom exceptions for task-related errors.
- Provides a common base exception for application-level task errors.

"tests/test_services.py"

- Tests task creation.
- Tests task completion.
- Tests invalid task titles.
- Tests attempts to access nonexistent tasks.

"pyproject.toml"

- Defines project metadata.
- Configures Ruff.
- Configures pytest.

Requirements

Before running the application, ensure you have:

- Python 3.11 or later.
- pip, Python's package installer.
- A terminal or command prompt.

Check your Python installation:

python --version

On some systems, you may need to use:

python3 --version

Installation

1. Clone the repository

If the project is hosted on GitHub:

git clone <repository-url>

Navigate into the project directory:

cd task_manager

Replace "<repository-url>" with your actual repository URL.

Alternatively, create the project directory manually and add the files shown in the project structure.

2. Create a virtual environment

A virtual environment keeps the project's dependencies separate from other Python projects.

Windows:

python -m venv .venv

Activate it using PowerShell:

.\.venv\Scripts\Activate.ps1

Or Command Prompt:

.venv\Scripts\activate.bat

Linux and macOS:

python3 -m venv .venv
source .venv/bin/activate

3. Install development dependencies

Install pytest and Ruff:

python -m pip install pytest ruff

These tools are used for testing, linting, and formatting.

Usage

Run the application from the project's root directory.

python -m app.main

The application displays a menu with the following options:

=== Task Manager ===

1. Add task
2. Complete task
3. View tasks
4. Exit

Choose an option:

Add a Task

Select option "1" and enter a task title.

Example:

Choose an option: 1
Task title: Learn Python OOP
Created task #1: Learn Python OOP

Empty task titles are rejected.

Complete a Task

Select option "2" and enter the ID of the task you want to complete.

Example:

Choose an option: 2
Task ID: 1
Completed: Learn Python OOP

If the task does not exist, the application displays an appropriate error.

View Tasks

Select option "3" to display all tasks and their current statuses.

Example:

[✓] 1. Learn Python OOP
[ ] 2. Practice type hints

The check mark indicates a completed task, while an empty space indicates a pending task.

Exit

Select option "4" to close the application.

Note: Tasks are stored in memory and are not saved between application sessions.

Example Output

A complete interaction might look like this:

=== Task Manager ===

1. Add task
2. Complete task
3. View tasks
4. Exit

Choose an option: 1
Task title: Learn Python
Created task #1: Learn Python

1. Add task
2. Complete task
3. View tasks
4. Exit

Choose an option: 1
Task title: Practice functions
Created task #2: Practice functions

1. Add task
2. Complete task
3. View tasks
4. Exit

Choose an option: 3
[ ] 1. Learn Python
[ ] 2. Practice functions

1. Add task
2. Complete task
3. View tasks
4. Exit

Choose an option: 2
Task ID: 1
Completed: Learn Python

1. Add task
2. Complete task
3. View tasks
4. Exit

Choose an option: 3
[✓] 1. Learn Python
[ ] 2. Practice functions

Architecture

The application follows a simple layered structure.

             User
               |
               v
          main.py
      User interaction
               |
               v
         services.py
       Business logic
               |
               v
         storage.py
       Data management
               |
               v
          models.py
       Task representation

The "errors.py" module defines custom exceptions used by the service and handled by the command-line interface.

Separation of Concerns

Each module has a distinct responsibility.

- The main module handles interaction.
- The service module handles business rules.
- The storage module manages task collections.
- The model module represents task data and behavior.
- The errors module defines meaningful application exceptions.

This separation reduces unnecessary dependencies and makes individual components easier to test.

Error Handling

The project uses custom exceptions to make failures easier to identify and handle.

Custom Exceptions

The following exceptions are defined in "app/errors.py":

Exception| Purpose
"TaskError"| Base exception for task-related errors
"TaskNotFoundError"| Raised when a requested task does not exist
"InvalidTaskTitleError"| Raised when a task title is empty

For example, attempting to complete a nonexistent task raises "TaskNotFoundError" rather than a generic exception.

The command-line interface also handles "ValueError" when a user enters an invalid number for a task ID.

Testing

The project uses pytest to verify the behavior of its service layer.

Run all tests from the project root:

python -m pytest

For more detailed output:

python -m pytest -v

The current tests cover:

- Successful task creation.
- Successful task completion.
- Rejection of empty task titles.
- Errors when completing nonexistent tasks.

Tests help ensure that changes do not accidentally break existing functionality.

Code Quality

Ruff is used for linting and formatting.

Check for linting errors

ruff check .

Automatically fix supported linting issues:

ruff check . --fix

Format the code

ruff format .

Check formatting without modifying files:

ruff format --check .

Recommended development workflow

Before committing changes, run:

ruff check .
ruff format --check .
python -m pytest

This checks for common code issues, verifies formatting, and runs the tests.

Learning Objectives

This project is designed to strengthen the following Python concepts.

Concept| Application
Functions| Reusable operations and UI helpers
Modules| Organizing code by responsibility
Object-oriented programming| Modeling tasks and services with classes
Dataclasses| Defining structured task objects
Enumerations| Representing task status
Type hints| Documenting parameters and return types
Encapsulation| Keeping internal storage details private
Exceptions| Communicating meaningful failures
Dependency injection| Passing storage into the service
Separation of concerns| Isolating UI, business logic, and storage
Unit testing| Verifying individual behaviors
Linting| Detecting common code problems
Formatting| Maintaining consistent code style

