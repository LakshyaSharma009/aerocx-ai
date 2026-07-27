package com.lakshya.focusflow;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Scanner;

public final class FocusFlowApp {
    private static final String HELP = "Commands: add \"title\" [low|medium|high], list [all|done], done <id>, delete <id>, help, exit";

    private FocusFlowApp() { }

    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(System.in)) {
            TaskService service = new TaskService(new TaskRepository(Path.of("data", "tasks.tsv")));
            System.out.println("FocusFlow — type 'help' for commands.");
            while (true) {
                System.out.print("focusflow> ");
                if (!scanner.hasNextLine()) break;
                String input = scanner.nextLine().trim();
                if (input.equalsIgnoreCase("exit")) break;
                try { handle(input, service); }
                catch (IllegalArgumentException | IOException exception) { System.out.println("Error: " + exception.getMessage()); }
            }
            System.out.println("Goodbye.");
        } catch (IOException exception) { System.err.println("Could not open task storage: " + exception.getMessage()); }
    }

    static void handle(String input, TaskService service) throws IOException {
        if (input.equalsIgnoreCase("help")) { System.out.println(HELP); return; }
        if (input.startsWith("add ")) {
            String[] parts = input.substring(4).trim().split("\\s+(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)");
            String rawTitle = parts[0].replaceAll("^\"|\"$", "");
            Task task = service.add(rawTitle, Priority.from(parts.length > 1 ? parts[1] : null));
            System.out.println("Added task #" + task.id() + "."); return;
        }
        if (input.startsWith("list")) { printTasks(service.list(input.length() > 4 ? input.substring(4).trim() : "open")); return; }
        if (input.startsWith("done ")) { System.out.println("Completed task #" + service.complete(parseId(input, "done")).id() + "."); return; }
        if (input.startsWith("delete ")) { service.delete(parseId(input, "delete")); System.out.println("Task deleted."); return; }
        throw new IllegalArgumentException("Unknown command. " + HELP);
    }

    private static int parseId(String input, String command) { return Integer.parseInt(input.substring(command.length()).trim()); }
    private static void printTasks(java.util.List<Task> tasks) {
        if (tasks.isEmpty()) { System.out.println("No tasks found."); return; }
        System.out.printf("%-4s %-7s %-9s %s%n", "ID", "STATUS", "PRIORITY", "TITLE");
        tasks.forEach(task -> System.out.printf("%-4d %-7s %-9s %s%n", task.id(), task.completed() ? "DONE" : "OPEN", task.priority(), task.title()));
    }
}
