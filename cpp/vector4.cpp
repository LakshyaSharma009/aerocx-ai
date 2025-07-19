#include<iostream>
#include<vector>
using namespace std;
void reversearray(vector<int> &vec,int size){
    int start=0;
    int end=size-1;
    while(start<end){
        swap(vec[start],vec[end]);
        start++;
        end--;
    }
}

int main(){
  vector<int> vec={4,1,3,4,8,10};
  reversearray(vec,vec.size());
  for(int val:vec){
    cout<<val<<endl;
  }
  
  

}