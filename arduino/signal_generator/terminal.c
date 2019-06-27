#include "terminal.h"

mks_header*   terminal_tx_header;
unsigned char terminal_tx_buffer[MAX_LENGTH];

mks_header*   terminal_rx_header;
unsigned char terminal_rx_buffer[MAX_LENGTH];

void
terminalInit(TerminalBuffers* buffers, hook_handlers* hookHandlers) {
	buffers->tx = terminal_tx_buffer;
	buffers->rx = terminal_rx_buffer;
	
	memset(terminal_tx_buffer, 0, MAX_LENGTH);
	memset(terminal_rx_buffer, 0, MAX_LENGTH);
	
	terminal_tx_header = (mks_header *)(&terminal_tx_buffer[0]);
	terminal_rx_header = (mks_header *)(&terminal_rx_buffer[0]);
	
	terminal_tx_header->magic_number[0] = 0xDE;
	terminal_tx_header->magic_number[1] = 0xAD;
}

void
dataArrived(TerminalBuffers* buffers, hook_handlers* hookHandlers, custom_opcode_callback callback) {
	if (checkMagic(buffers)) {
		switch (terminal_rx_header->op_code) {
			case OPCODE_GET_CONFIG_REGISTER: {
			}
			break;
			case OPCODE_SET_CONFIG_REGISTER: {
			}
			break;
			case OPCODE_GET_BASIC_SENSOR_VALUE: {
			}
			break;
			case OPCODE_SET_BASIC_SENSOR_VALUE: {
			}
			break;
			case OPCODE_PAUSE_WITH_TIMEOUT: {
			}
			break;
			case OPCODE_GET_DEVICE_TYPE: {
				getDeviceType(buffers, hookHandlers);
			}
			break;
			case OPCODE_GET_DEVICE_UUID: {
				getDeviceUUID(buffers, hookHandlers);
			}
			break;
			default: {
				callback(terminal_rx_header->op_code, &terminal_rx_buffer);
			}
			break;
		}
		// memset(terminal_rx_buffer, 0, MAX_LENGTH);
	} else {
		
	}
}

unsigned char
checkMagic(TerminalBuffers* buffers) {
	return (terminal_rx_buffer[0] == 0xDE && terminal_rx_buffer[1] == 0xAD);
}

void
getDeviceType(TerminalBuffers* buffers, hook_handlers* hookHandlers) {
	unsigned char tx_buffer_length		= sizeof(mks_header) + buffers->deviceTypeLen;
	terminal_tx_header->op_code        	= OPCODE_GET_DEVICE_TYPE;
	terminal_tx_header->content_length 	= buffers->deviceTypeLen;
	
	memcpy((unsigned char *)&terminal_tx_buffer[sizeof(mks_header)], buffers->deviceType, buffers->deviceTypeLen);
	
	terminal_tx_buffer[tx_buffer_length] = '\n';
	hookHandlers->terminalPrint((unsigned char *)&terminal_tx_buffer[0], tx_buffer_length + 1);
}

void
getDeviceUUID(TerminalBuffers* buffers, hook_handlers* hookHandlers) {
	unsigned char tx_buffer_length		= sizeof(mks_header) + buffers->uuidLen;
	terminal_tx_header->op_code        	= OPCODE_GET_DEVICE_UUID;
	terminal_tx_header->content_length 	= buffers->uuidLen;

	memcpy((unsigned char *)&terminal_tx_buffer[sizeof(mks_header)], buffers->uuid, buffers->uuidLen);

	terminal_tx_buffer[tx_buffer_length] = '\n';
	hookHandlers->terminalPrint((unsigned char *)&terminal_tx_buffer[0], tx_buffer_length + 1);
}
