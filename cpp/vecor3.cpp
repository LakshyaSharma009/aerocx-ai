#include<iostream>
#include<vector>
using namespace std;
int linearSearch(vector<int> &vec,int size,int target){
    for(int i=0;i<size;i++){
        if(vec[i]==target){
            return i;
        }
    }
    return -1;
}

int main(){
  vector<int> vec={4,1,3,4,8,10};
  int x=linearSearch(vec,vec.size(),10);
  cout<<x;
  
  

}