#include<iostream>
#include<vector>
#include <algorithm>
using namespace std;
int majority(vector<int> &nums){
    sort(nums.begin(),nums.end());
    int freq=1;
    int ans=nums[0];
    
    int n=nums.size();
    for(int i=1;i<n;i++){
        if(nums[i]==nums[i-1]){
         freq++;}
       else{
        freq=1;
        ans=nums[i];
        
       }
       if(freq>n/2)
        {return ans;}
    }
    return 0;
}
int main(){
    vector<int> nums={1,2,2,2,1,1,2,2,5};
    
    cout<<majority(nums);
  
    

    
}
