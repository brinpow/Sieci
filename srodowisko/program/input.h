#pragma once

#include <cstdio>
#include <string>

#include <lzma.h>

bool init_decoder(lzma_stream *strm);
bool decompress(lzma_stream *strm, const char *inname, FILE *infile, std::string& content);
