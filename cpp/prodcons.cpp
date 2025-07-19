#include <stdio.h>
#include <stdlib.h>

int mutex = 1;
int full = 0;
int empty = 5;
int x = 0;

void producer() {
  if ((mutex == 1) && (empty != 0)) {
    mutex = 0;
    full++;
    empty--;
    x++;
    printf("Producer produced item %d\n", x);
    mutex = 1;
  } else {
    printf("Buffer Full or Mutex Locked\n");
  }
}

void consumer() {
  if ((mutex == 1) && (full != 0)) {
    mutex = 0;
    printf("Consumer consumed item %d\n", x);
    x--;
    full--;
    empty++;
    mutex = 1;
  } else {
    printf("Buffer Empty or Mutex Locked\n");
  }
}

int main() {
  int ch;
  printf("1. Producer\n2. Consumer\n3. Exit\n");

  while (1) {
    printf("Enter your choice: ");
    scanf("%d", &ch);

    switch (ch) {
      case 1:
        producer();
        break;
      case 2:
        consumer();
        break;
      case 3:
        exit(0);
      default:
        printf("Invalid Choice\n");
    }
  }

  return 0;
}
