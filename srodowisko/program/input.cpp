#include <cstdbool>
#include <cstdlib>
#include <cstring>
#include <cerrno>

#include "input.h"

bool init_decoder(lzma_stream *strm) {
    lzma_ret ret = lzma_stream_decoder(strm, UINT64_MAX, LZMA_CONCATENATED);
    if (ret == LZMA_OK)
        return true;
    const char *msg;
    switch (ret) {
    case LZMA_MEM_ERROR:
        msg = "Memory allocation failed";
        break;
    case LZMA_OPTIONS_ERROR:
        msg = "Unsupported decompressor flags";
        break;
    default:
        msg = "Unknown error, possibly a bug";
        break;
    }
    fprintf(stderr, "Error initializing the decoder: %s (error code %u)\n", msg, ret);
    return false;
}


bool decompress(lzma_stream *strm, const char *inname, FILE *infile, std::string& content) {
    lzma_action action = LZMA_RUN;

    char inbuf[BUFSIZ];
    char outbuf[BUFSIZ];

    strm->next_in = NULL;
    strm->avail_in = 0;
    strm->next_out = (uint8_t*)outbuf;
    strm->avail_out = sizeof(outbuf);

    while (true) {
        if (strm->avail_in == 0 && !feof(infile)) {
            strm->next_in = (const uint8_t*)inbuf;
            strm->avail_in = fread(inbuf, 1, sizeof(inbuf), infile);

            if (ferror(infile)) {
                fprintf(stderr, "%s: Read error: %s\n", inname, strerror(errno));
                return false;
            }
            if (feof(infile))
                action = LZMA_FINISH;
        }

        lzma_ret ret = lzma_code(strm, action);

        if (strm->avail_out == 0 || ret == LZMA_STREAM_END) {
            size_t write_size = sizeof(outbuf) - strm->avail_out;
            content.append(outbuf, write_size);
            strm->next_out = (uint8_t*)outbuf;
            strm->avail_out = sizeof(outbuf);
        }

        if (ret != LZMA_OK) {
            if (ret == LZMA_STREAM_END)
                return true;
            const char *msg;
            switch (ret) {
            case LZMA_MEM_ERROR:
                msg = "Memory allocation failed";
                break;
            case LZMA_FORMAT_ERROR:
                msg = "The input is not in the .xz format";
                break;
            case LZMA_OPTIONS_ERROR:
                msg = "Unsupported compression options";
                break;
            case LZMA_DATA_ERROR:
                msg = "Compressed file is corrupt";
                break;
            case LZMA_BUF_ERROR:
                msg = "Compressed file is truncated or "
                        "otherwise corrupt";
                break;
            default:
                msg = "Unknown error, possibly a bug";
                break;
            }
            fprintf(stderr, "%s: Decoder error: %s (error code %u)\n", inname, msg, ret);
            return false;
        }
    }
}
