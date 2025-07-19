#include<iostream>
#include<climits>
#define INT_MIN (-2147483648)

using namespace std;



int main() {
    int arr[] = {1, 2, 3, 1,-2, 5, 4};
    int n=sizeof(arr)/sizeof(arr[0]);
    int maxsum=INT_MIN;
    for(int st=0;st<n;st++){
        int cursum=0;
        for(int end=st;end<n;end++){
            cursum+=arr[end];
            maxsum=max(cursum,maxsum);
        }
    }
    cout<<maxsum<<endl;
    
    return 0;
}
