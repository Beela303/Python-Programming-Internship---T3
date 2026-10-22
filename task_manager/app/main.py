from app.errors import TaskError
from app.services import TaskService
from app.storage import TaskStorage


def display_tasks(service: TaskService) -> None:
    tasks = service.get_tasks()

    if not tasks:
        print("No tasks yet.")
        return

    for task in tasks:
        status = "✓" if task.is_completed() else " "
        print(f"[{status}] {task.id}. {task.title}")


def main() -> None:
    storage = TaskStorage()
    service = TaskService(storage)

    print("=== Task Manager ===")

    while True:
        print("\n1. Add task")
        print("2. Complete task")
        print("3. View tasks")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                title = input("Task title: ")
                task = service.create_task(title)
                print(f"Created task #{task.id}: {task.title}")

            elif choice == "2":
                task_id = int(input("Task ID: "))
                task = service.complete_task(task_id)
                print(f"Completed: {task.title}")

            elif choice == "3":
                display_tasks(service)

            elif choice == "4":
                print("Goodbye!")
                break

            else:
                print("Invalid option.")

        except ValueError:
            print("Please enter a valid number.")

        except TaskError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()