#include<iostream>
#include<vector>
using namespace std;

int main(){
  vector<int> vec;
  vec.push_back(25);
  vec.push_back(35);
  vec.push_back(45);
  cout<<vec.size()<<endl;
  vec.pop_back();
  cout<<vec.front()<<endl;

  cout<<vec.at(1);
  

}