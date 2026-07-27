# FocusFlow

FocusFlow is a lightweight Java command-line task manager. It stores tasks locally, supports priorities, and keeps the interface deliberately fast and simple.

## Features

- Add tasks with `low`, `medium`, or `high` priority
- List open tasks, completed tasks, or all tasks
- Mark tasks complete and delete tasks by ID
- Persist data in a local `data/tasks.tsv` file
- Run as a friendly interactive shell or with one-shot commands

## Requirements

- Java 17 or later
- Maven 3.9 or later

## Run it

```bash
mvn clean package
java -jar target/focusflow-1.0.0.jar
```

### Example session

```text
focusflow> add "Submit project report" high
Added task #1.
focusflow> list
ID   STATUS  PRIORITY  TITLE
1    OPEN    HIGH      Submit project report
focusflow> done 1
Completed task #1.
```

## Commands

| Command | Description |
| --- | --- |
| `add "title" [priority]` | Add a task; priority defaults to `medium` |
| `list [all|done]` | List open tasks (default), all tasks, or done tasks |
| `done <id>` | Mark a task complete |
| `delete <id>` | Permanently remove a task |
| `help` | Show the command reference |
| `exit` | Close FocusFlow |

## Development

```bash
mvn test
mvn clean package
```

The project uses only the Java standard library at runtime. JUnit 5 is used for tests.

## License

Released under the [MIT License](LICENSE).
