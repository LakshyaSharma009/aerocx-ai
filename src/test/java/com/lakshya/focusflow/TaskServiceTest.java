package com.lakshya.focusflow;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class TaskServiceTest {
    @TempDir Path directory;

    @Test void addsPersistsAndCompletesATask() throws Exception {
        Path file = directory.resolve("tasks.tsv");
        TaskService service = new TaskService(new TaskRepository(file));
        Task task = service.add("Ship FocusFlow", Priority.HIGH);
        assertEquals(1, task.id());
        assertEquals(1, Files.readAllLines(file).size());

        service.complete(task.id());
        TaskService reloaded = new TaskService(new TaskRepository(file));
        assertTrue(reloaded.list("done").get(0).completed());
    }

    @Test void rejectsUnknownTask() throws Exception {
        TaskService service = new TaskService(new TaskRepository(directory.resolve("tasks.tsv")));
        assertThrows(IllegalArgumentException.class, () -> service.delete(99));
    }
}
