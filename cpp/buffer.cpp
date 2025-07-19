#include <stdio.h>
#include <string.h>

void secret() {
    printf("💀 Secret function accessed! You’ve been hacked!\n");
}

void vulnerable() {
    char buffer[50];

    printf("Enter some text: ");
    gets(buffer);  // 🚨 VERY DANGEROUS! gets() does NOT check bounds!

    printf("You entered: %s\n", buffer);
}

int main() {
    vulnerable();
    return 0;
}

