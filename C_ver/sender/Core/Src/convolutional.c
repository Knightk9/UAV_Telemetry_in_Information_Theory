#include "convolutional.h"

uint32_t Process_Channel_Coding(uint8_t *input_bytes, uint32_t input_len_bytes, uint8_t *output_buffer) {
    uint32_t total_bits = input_len_bytes * 8;
    uint32_t out_bit_ptr = 0;

    uint8_t shift_reg = 0;

    for (uint32_t i = 0; i < total_bits + 2; i++) {
        uint8_t current_bit = 0;
        if (i < total_bits) {
            uint32_t byte_idx = i / 8;
            uint8_t bit_idx = 7 - (i % 8);
            current_bit = (input_bytes[byte_idx] >> bit_idx) & 0x01;
        } else {
            current_bit = 0;
        }

        shift_reg = ((shift_reg << 1) | current_bit) & 0x07;

        uint8_t b0 = (shift_reg >> 2) & 0x01;
        uint8_t b1 = (shift_reg >> 1) & 0x01;
        uint8_t b2 = shift_reg & 0x01;

        uint8_t out1 = b0 ^ b1 ^ b2;
        uint8_t out2 = b0 ^ b2;
        uint8_t out3 = b0 ^ b1;

        uint8_t outputs[3] = {out1, out2, out3};

        for (int j = 0; j < 3; j++) {
            uint32_t out_byte_pos = out_bit_ptr / 8;
            uint8_t out_bit_pos = 7 - (out_bit_ptr % 8);

            if (outputs[j]) {
                output_buffer[out_byte_pos] |= (1 << out_bit_pos);
            } else {
                output_buffer[out_byte_pos] &= ~(1 << out_bit_pos);
            }
            out_bit_ptr++;
        }
    }

    return (out_bit_ptr + 7) / 8;
}
