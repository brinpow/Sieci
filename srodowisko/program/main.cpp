#include <iostream>
#include <sstream>

#include "input.h"
#include "matrix.h"

int main(int argc, char** argv)
{
    if (argc <= 1) {
        fprintf(stderr, "Usage: %s FILES...\n", argv[0]);
        return EXIT_FAILURE;
    }

    lzma_stream strm = LZMA_STREAM_INIT;

    bool success = true;

    for (int i = 1; i < argc; ++i) {
        if (!init_decoder(&strm)) {
            success = false;
            break;
        }
        FILE *infile = fopen(argv[i], "rb");
        if (infile == NULL) {
            fprintf(stderr, "%s: Error opening the input file: %s\n", argv[i], strerror(errno));
            success = false;
        } else {
            std::string content;
            success &= decompress(&strm, argv[i], infile, content);

            std::stringstream sin(content);
            int N;
            sin >> N;
            Eigen::VectorXd v(N);
            for ( uint i = 0 ; i < N ; i++ ) {
                sin >> v(i);
            }
            Eigen::MatrixXd M(N,N);
            for ( uint i = 0 ; i < N ; i++ )
                for ( uint j = 0 ; j < N ; j++ ) {
                    sin >> M(i,j);
                }

            std::cout << operate(M, v) << std::endl;
        }
        fclose(infile);
    }
    lzma_end(&strm);
    return success ? EXIT_SUCCESS : EXIT_FAILURE;
}
