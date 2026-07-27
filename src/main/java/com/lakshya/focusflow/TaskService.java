package com.lakshya.focusflow;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;

public class TaskService {
    private final TaskRepository repository;
    private final List<Task> tasks;

    public TaskService(TaskRepository repository) throws IOException {
        this.repository = repository;
        this.tasks = repository.load();
    }

    public Task add(String title, Priority priority) throws IOException {
        int nextId = tasks.stream().mapToInt(Task::id).max().orElse(0) + 1;
        Task task = new Task(nextId, title.trim(), priority, false, LocalDateTime.now());
        tasks.add(task); save(); return task;
    }

    public List<Task> list(String filter) {
        return tasks.stream().filter(task -> switch (filter) {
            case "done" -> task.completed();
            case "all" -> true;
            default -> !task.completed();
        }).sorted(Comparator.comparing(Task::completed).thenComparing(Task::priority).thenComparing(Task::id)).toList();
    }

    public Task complete(int id) throws IOException { return replace(id, Task::complete); }

    public void delete(int id) throws IOException {
        if (!tasks.removeIf(task -> task.id() == id)) throw new IllegalArgumentException("No task exists with ID " + id + ".");
        save();
    }

    private Task replace(int id, java.util.function.UnaryOperator<Task> update) throws IOException {
        for (int i = 0; i < tasks.size(); i++) if (tasks.get(i).id() == id) {
            Task changed = update.apply(tasks.get(i)); tasks.set(i, changed); save(); return changed;
        }
        throw new IllegalArgumentException("No task exists with ID " + id + ".");
    }

    private void save() throws IOException { repository.save(tasks); }
}
