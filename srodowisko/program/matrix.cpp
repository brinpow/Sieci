#include <algorithm>

#include "matrix.h"


bool find(double* a, size_t l, size_t h, double v) {
    auto m = (l+h-1)/2;
    if ( a[m] <= v )
        return find(a, m+1, h, v);
    if ( h <= l )
        return a[l] == v;
    return find(a, l, m, v);
}






Eigen::VectorXd operate(const Eigen::MatrixXd& m, const Eigen::VectorXd& v) {
    Eigen::VectorXd u = m*v;

    std::sort(u.data(), u.data()+u.size());

    if ( find(u.data(), 0, u.size(), 0) )
        return u+u;

    return u;
}
