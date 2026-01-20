"""Main CLI interface for Todo application."""

import sys
from datetime import datetime

from ..models.todo import TodoStatus
from ..services.todo_service import (
    AlreadyCompletedError,
    InvalidTitleError,
    TodoNotFoundError,
    TodoService,
)


# =============================================================================
# CLI Helper Functions
# =============================================================================


def format_todo(todo) -> str:
    """Format todo for display.

    Args:
        todo: Todo object to format

    Returns:
        Formatted string representation
    """
    description = todo.description if todo.description else "No description"
    created_str = todo.created_at.strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"ID: {todo.id}\n"
        f"Title: {todo.title}\n"
        f"Description: {description}\n"
        f"Status: {todo.status.value}\n"
        f"Created: {created_str}"
    )


def format_todo_list_item(todo) -> str:
    """Format todo for list display.

    Args:
        todo: Todo object to format

    Returns:
        Formatted string for list view
    """
    return f"ID: {todo.id} | Title: {todo.title} | Status: {todo.status.value}"


# =============================================================================
# CLI Commands
# =============================================================================


def cmd_create_todo(service: TodoService) -> None:
    """Create a new todo.

    Args:
        service: TodoService instance
    """
    print("\n=== Create Todo ===")
    title = input("Enter title (required): ").strip()

    if not title:
        print("\nERROR: Title cannot be empty.")
        return

    description = input("Enter description (optional, press Enter to skip): ").strip()
    description = description if description else None

    try:
        todo = service.create_todo(title, description)
        print("\n=== Todo Created Successfully ===")
        print(format_todo(todo))
    except (InvalidTitleError, Exception) as e:
        print(f"\nERROR: {e}")


def cmd_list_todos(service: TodoService) -> None:
    """List all todos.

    Args:
        service: TodoService instance
    """
    print("\n=== Your Todos ===")
    todos = service.list_todos()

    if not todos:
        print("\nNo todos found.")
        return

    for todo in todos:
        print(format_todo_list_item(todo))


def cmd_view_todo(service: TodoService) -> None:
    """View details of a specific todo.

    Args:
        service: TodoService instance
    """
    print("\n=== View Todo ===")
    todo_id_str = input("Enter todo ID: ").strip()

    try:
        todo_id = int(todo_id_str)
    except ValueError:
        print("\n❌ Error: Todo ID must be a number.")
        return

    try:
        todo = service.get_todo_by_id(todo_id)
        print("\n=== Todo Details ===")
        print(format_todo(todo))
    except TodoNotFoundError as e:
        print(f"\nERROR: {e}")


def cmd_update_todo(service: TodoService) -> None:
    """Update an existing todo.

    Args:
        service: TodoService instance
    """
    print("\n=== Update Todo ===")
    todo_id_str = input("Enter todo ID: ").strip()

    try:
        todo_id = int(todo_id_str)
    except ValueError:
        print("\n❌ Error: Todo ID must be a number.")
        return

    # First, retrieve the todo to show current values
    try:
        current_todo = service.get_todo_by_id(todo_id)
    except TodoNotFoundError as e:
        print(f"\nERROR: {e}")
        return

    print(f"\nCurrent title: {current_todo.title}")
    new_title = input("Enter new title (press Enter to keep current): ").strip()

    print(f"\nCurrent description: {current_todo.description or 'No description'}")
    new_description = input("Enter new description (press Enter to keep current): ").strip()
    new_description = new_description if new_description else None

    # If user provided empty input for both, nothing to update
    if not new_title and new_description is None:
        print("\nNo changes provided.")
        return

    try:
        updated_todo = service.update_todo(
            todo_id,
            title=new_title if new_title else None,
            description=new_description,
        )
        print("\n✅ Todo updated successfully!")
        print(format_todo(updated_todo))
    except (TodoNotFoundError, InvalidTitleError, Exception) as e:
        print(f"\nERROR: {e}")


def cmd_complete_todo(service: TodoService) -> None:
    """Mark a todo as completed.

    Args:
        service: TodoService instance
    """
    print("\n=== Complete Todo ===")
    todo_id_str = input("Enter todo ID: ").strip()

    try:
        todo_id = int(todo_id_str)
    except ValueError:
        print("\n❌ Error: Todo ID must be a number.")
        return

    try:
        todo = service.complete_todo(todo_id)
        print("\n✅ Todo marked as completed!")
        print(format_todo(todo))
    except AlreadyCompletedError as e:
        print(f"\nERROR: {e}")
    except TodoNotFoundError as e:
        print(f"\nERROR: {e}")


def cmd_delete_todo(service: TodoService) -> None:
    """Delete a todo.

    Args:
        service: TodoService instance
    """
    print("\n=== Delete Todo ===")
    todo_id_str = input("Enter todo ID: ").strip()

    try:
        todo_id = int(todo_id_str)
    except ValueError:
        print("\n❌ Error: Todo ID must be a number.")
        return

    try:
        service.delete_todo(todo_id)
        print(f"\n✅ Todo {todo_id} deleted successfully!")
    except TodoNotFoundError as e:
        print(f"\nERROR: {e}")


# =============================================================================
# Main Menu
# =============================================================================


def main_menu(service: TodoService) -> None:
    """Display main menu and handle user choices.

    Args:
        service: TodoService instance
    """
    while True:
        print("\n" + "=" * 40)
        print("=== Todo App ===")
        print("=" * 40)
        print("1. Create Todo")
        print("2. List Todos")
        print("3. View Todo")
        print("4. Update Todo")
        print("5. Complete Todo")
        print("6. Delete Todo")
        print("7. Exit")
        print("=" * 40)

        choice = input("\nEnter choice (1-7): ").strip()

        if choice == "1":
            cmd_create_todo(service)
        elif choice == "2":
            cmd_list_todos(service)
        elif choice == "3":
            cmd_view_todo(service)
        elif choice == "4":
            cmd_update_todo(service)
        elif choice == "5":
            cmd_complete_todo(service)
        elif choice == "6":
            cmd_delete_todo(service)
        elif choice == "7":
            print("\n=== Goodbye! ===")
            sys.exit(0)
        else:
            print("\nERROR: Invalid choice. Please enter a number between 1 and 7.")


# =============================================================================
# Entry Point
# =============================================================================


def main() -> None:
    """Main entry point for the CLI application."""
    print("Welcome to Phase-1 In-Memory Todo App!")
    print("All data is stored in memory and will be lost on exit.\n")

    service = TodoService()
    main_menu(service)


if __name__ == "__main__":
    main()
