#include <stdio.h>
#include <stdlib.h>

int nwd(int a, int b) {
    int t;
    while(a) {  //should be while(b)
        if (a<b)
            t=a;
        else
            t = a % b;
        a = b;
        b = t;
    }
    return a;
}

int main(int argc, char** argv) {
    if (argc!=3) {
        printf("Invalid argument count\n");
        return -1;
    }
    int a = atoi(argv[1]);
    int b = atoi(argv[2]);
    int result = nwd(a,b);
    printf("%d\n",result);
    return 0;
}

