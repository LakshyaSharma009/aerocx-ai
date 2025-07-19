#include <stdio.h>
#include <stdlib.h>

int main()
{
  int blocks = 8;
  int memory_space[8] = {10,4,20,18,7,9,12,15};
  
  int processes = 3;
  int process_space[3] = {12, 10, 9};
  
  for(int i = 0; i < processes; i++)
  {
    int worstFitIdx = -1;
    
    for(int j = 0; j < blocks; j++)
    {
      if(memory_space[j] >= process_space[i] && memory_space[j] > memory_space[worstFitIdx])
        worstFitIdx = j;
    }
    
    if(worstFitIdx != -1)
    {
      memory_space[worstFitIdx] -= process_space[i];
      printf("Process %d : Process Size %d : Block No %d\n", i+1, process_space[i], worstFitIdx+1);
    }
    else
    {
      printf("Not Possible to allocate %d", i);
    }
  }
  
  return 0;
  
}