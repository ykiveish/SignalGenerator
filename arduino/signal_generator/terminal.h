#ifndef TERMINAL_H
#define TERMINAL_H

#pragma once

#include "MkSProtocol.h"

typedef struct {
	unsigned char*	tx;
	unsigned int	txLen;
	unsigned char*	rx;
	unsigned int	rxLen;
	unsigned char*	uuid;
	unsigned int	uuidLen;
	unsigned char*	deviceType;
	unsigned int	deviceTypeLen;
	unsigned char*	deviceName;
	unsigned int	deviceNameLen;
} TerminalBuffers;

#ifdef __cplusplus
extern "C"
{
#endif
void terminalInit(TerminalBuffers* buffers, hook_handlers* hookHandlers);
void dataArrived(TerminalBuffers* buffers, hook_handlers* hookHandlers, custom_opcode_callback callback);
unsigned char checkMagic(TerminalBuffers* buffers);

void getDeviceType(TerminalBuffers* buffers, hook_handlers* hookHandlers);
void getDeviceUUID(TerminalBuffers* buffers, hook_handlers* hookHandlers);
#ifdef __cplusplus
}
#endif

#endif /* TERMINAL_H */