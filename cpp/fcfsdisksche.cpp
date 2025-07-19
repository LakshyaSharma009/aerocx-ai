#include <stdio.h>
#include <stdlib.h>

int main()
{
  
  int n;
  printf("Enter the number of Disk Requests: ");
  scanf("%d", &n);
  
  int disks[n];
  printf("Enter the disk sequence: ");
  for(int i = 0; i < n; i++)
    scanf("%d",&disks[i]);
  
  int head;
  printf("Enter the head position: ");
  scanf("%d", &head);
  
  int total_movement = 0;
  
  printf("%d --> ", head);
  for(int i = 0; i < n; i++)
  {
    total_movement += abs(disks[i] - head);
    head = disks[i];
    
    printf("%d --> ", disks[i]);
  }
  
  printf("\nTotal Movement : %d cylinders\n", total_movement);
  
  return 0;
}