package com.lakshya.focusflow;

import java.util.Locale;

public enum Priority {
    LOW, MEDIUM, HIGH;

    public static Priority from(String value) {
        try {
            return value == null ? MEDIUM : valueOf(value.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException exception) {
            throw new IllegalArgumentException("Priority must be low, medium, or high.");
        }
    }
}
