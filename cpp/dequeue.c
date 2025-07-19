#include<stdio.h>
#define SIZE 5
void deqinsr(int*,int[]);
int deqdelf(int*, int *,int[]);
void deqdis(int,int,int[]);
void deqdelr(int*, int[]);
void deqinsf(int*,int[]);
void main()
{
  int r=-1,f=0,ch, deq[SIZE];
  while(1)
  {
   printf("\n1:Insert-Rear 2:Delete-Front");
   printf("\n3:Delete-Rear 4:Insert-Front 5:Display\n");
   scanf("%d",&ch);
   switch(ch)
   {
    case 1:deqinsr(&r,deq); break;
    case 2:deqdelf(&f,&r,deq); break;
    case 3:deqdelr(&r,deq);break;
    case 4:deqinsf(&f,deq);break;
    case 5:deqdis(f,r,deq);break;
    default:printf("Not a valid operation");
	    getch(); exit(0);
   }
  }
}

void deqdis(int f, int r, int deq[])
{
  int i;
  if(f>r)
  printf("Queue is Empty");
  else
  {
   printf("The status of Queue is\n");
   for(i=f;i<=r;i++)
   printf("%d ",deq[i]);
  }
}

int deqdelf(int *f, int *r,int deq[])
{
 if(*f>*r)
 printf("Queue is Empty");
 else
 {
  printf("The deleted element is %d",deq[*f]);
  *f=*f+1;
 }
 return 0;
}


void deqinsr(int *r,int deq[])
{
  int element;
  if(*r==SIZE-1)
  printf("Queue is Full");
  else
  {
   printf("Enter the element \n");
   scanf("%d",&element);
   *r=*r+1;
   deq[*r]=element;
  }
}

void deqdelr(int *r, int deq[])
{
 if(*r==0)
 printf("Queue is Empty");
 else
 {
  printf("\nThe deleted element is %d",deq[*r]);
  *r=*r-1;
 }
}

void deqinsf(int *f, int deq[])
{
 int ele;
 if(*f==0)
 printf("Queue is Full");
 else
 {
  printf("Enter the element\n");
  scanf("%d",&ele);
  *f=*f-1;
  deq[*f]=ele;
 }
}