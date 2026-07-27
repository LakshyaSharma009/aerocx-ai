package com.lakshya.focusflow;

import java.time.LocalDateTime;
import java.util.Objects;

public record Task(int id, String title, Priority priority, boolean completed, LocalDateTime createdAt) {
    public Task {
        if (id < 1) throw new IllegalArgumentException("Task ID must be positive.");
        if (title == null || title.isBlank()) throw new IllegalArgumentException("Task title cannot be empty.");
        Objects.requireNonNull(priority, "priority");
        Objects.requireNonNull(createdAt, "createdAt");
    }

    public Task complete() {
        return new Task(id, title, priority, true, createdAt);
    }
}
