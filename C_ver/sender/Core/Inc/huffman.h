#ifndef __HUFFMAN_H
#define __HUFFMAN_H

#include "main.h"

typedef struct {
    int16_t symbol;
    uint32_t freq;
    uint8_t code_len;
    uint32_t code;
} SymbolCode_t;

typedef struct Node {
    int16_t symbol;
    uint32_t freq;
    struct Node *left;
    struct Node *right;
} HuffmanNode_t;

void Process_Source_Coding(int32_t data_in[3][101], DataPacket_t *packet);

#endif
