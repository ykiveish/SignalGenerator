#ifndef MKSPROTOCOL_H
#define MKSPROTOCOL_H

#pragma once

#include <stdint.h>

#define MAX_LENGTH 									512
#define OPCODE_GET_CONFIG_REGISTER                  0x1
#define OPCODE_SET_CONFIG_REGISTER                  0x2
#define OPCODE_GET_BASIC_SENSOR_VALUE               0x3
#define OPCODE_SET_BASIC_SENSOR_VALUE               0x4
#define OPCODE_PAUSE_WITH_TIMEOUT                   0x5

#define OPCODE_GET_DEVICE_TYPE                      0x50
#define OPCODE_GET_DEVICE_UUID                      0x51

typedef void (*terminal_print_hook)(unsigned char * buffer, uint16_t len);
typedef void (*debug_print_hook)(uint8_t * data);
typedef void (*custom_opcode_callback)(uint16_t opcode, uint8_t * data);

typedef struct {
	terminal_print_hook 	terminalPrint;
	debug_print_hook 		debugPrint;
} hook_handlers;

typedef struct {
  unsigned char   magic_number[2];
  unsigned short  op_code;
  unsigned short  content_length;
} mks_header;

#endif /* MKSPROTOCOL_H */