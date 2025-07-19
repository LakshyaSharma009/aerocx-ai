#include<iostream>
using namespace std;
int main(){
    int arr[3][3]={1,2,3,5,6,6,7,8,9};
    int sum=0;
    for(int i=0;i<3;i++){
        for(int j=0;j<3;j++){
            if(i==j)
            sum=sum+arr[i][j];
        }
    }
    cout<<sum;
}