#include <iostream>
using namespace std;

bool isIdealGenerator(int k) {
    if (k == 1) return true;
    if (k % 2 == 0) return false;
    return true;
}

int main() {
    int t;
    cin >> t;
    
    while (t--) {
        int k;
        cin >> k;
        if (isIdealGenerator(k)) cout << "YES" << endl;
        else cout << "NO" << endl;
    }
    
    return 0;
}
