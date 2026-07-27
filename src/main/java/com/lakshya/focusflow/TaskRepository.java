package com.lakshya.focusflow;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

public class TaskRepository {
    private final Path file;

    public TaskRepository(Path file) { this.file = file; }

    public List<Task> load() throws IOException {
        if (!Files.exists(file)) return new ArrayList<>();
        List<Task> tasks = new ArrayList<>();
        for (String line : Files.readAllLines(file)) {
            String[] parts = line.split("\\t", -1);
            if (parts.length != 5) continue;
            tasks.add(new Task(Integer.parseInt(parts[0]), parts[1].replace("\\n", "\n"),
                    Priority.valueOf(parts[2]), Boolean.parseBoolean(parts[3]), LocalDateTime.parse(parts[4])));
        }
        return tasks;
    }

    public void save(List<Task> tasks) throws IOException {
        Path parent = file.getParent();
        if (parent != null) Files.createDirectories(parent);
        List<String> lines = tasks.stream().map(task -> String.join("\t", String.valueOf(task.id()),
                task.title().replace("\n", "\\n").replace("\t", " "), task.priority().name(),
                String.valueOf(task.completed()), task.createdAt().toString())).toList();
        Files.write(file, lines);
    }
}
