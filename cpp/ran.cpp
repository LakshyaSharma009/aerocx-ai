#include<iostream>
#include<cstdlib> // Required for rand() and srand()
#include<ctime>   // Required for time()
using namespace std;

int main(){
    srand(time(0)); // Seed the random number generator with current time
    int i;
    i = rand() % 5; // Generate a random number between 0 and 4
    cout << i + 1;  // Adjust to get a number between 1 and 5
    return 0;
}
