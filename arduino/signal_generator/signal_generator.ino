#include "terminal.h"

#define OPCODE_SIGNAL_GENERATION_CONFIG 	0x500
#define OPCODE_SIGNAL_GENERATION_START 		0x501
#define OPCODE_SIGNAL_GENERATION_BUFFER 	0x502
#define OPCODE_SIGNAL_GENERATION_STOP 		0x503

#define TRUE 	0x1
#define FALSE 	0x0

/*
 * System defienition area (DO NOT CHANGE)
 */
unsigned char MKS_UUID[] = { 'a','c','6','d','e','8','3','7','-',
                         '7','8','6','3','-',
                         '7','2','a','9','-',
                         'c','7','8','9','-',
                         'b','0','a','a','e','7','e','9','d','9','3','e' };
unsigned char MKS_DEVICE_TYPE_NAME[] = { 'A','T','M','E','G','A','3','2','8' };
unsigned char MKS_DEVICE_TYPE[] = { '1','2','3','4'};

hook_handlers 	hookHandlers;
TerminalBuffers terminalBuffers;

void arduinoDebugPrintHookHandler(uint16_t opcode, uint8_t * buffer);
void arduinoTerminalPrintHookHandler(unsigned char * buffer, uint16_t len);

/*
 * System defienition area (DO NOT CHANGE)
 */
 
typedef struct {
	uint8_t 	pinId;
	uint16_t 	signalsCount;
	uint16_t	interval;
} SignalGenerationConfigHeader;

typedef struct {
	uint16_t 	signalsCount;
	uint8_t		buffer;
} SignalGenerationBufferHeader;

void blink(void);
void setTimerValue(uint16_t prescaler);
void startTimer(void);
void stopTimer(void);
void customOpcodeHandler(uint8_t * data);

const int signal_an_pin = A0;
const int signal_pin = PB5;
const int debug_pin = PB4;
const int debug2_pin = PB3;
const int debug3_pin = PB2;
const uint16_t t1_comp = 24;

uint8_t*	signalBuffer;
uint16_t 	bufferIndex 			= 0;
uint16_t	bufferSize 				= 0;
uint8_t 	amplitude 				= 0;
uint8_t		signalGeneratorWorking 	= FALSE;

void setup() {
	Serial.begin(115200);
	pinMode(signal_an_pin, OUTPUT);
	pinMode(13, OUTPUT);
	pinMode(12, OUTPUT);
	pinMode(11, OUTPUT);
	pinMode(10, OUTPUT);
	pinMode(9, OUTPUT);
	
	/*
	 * System defienition area (DO NOT CHANGE)
	 */
	hookHandlers.terminalPrint 	= arduinoTerminalPrintHookHandler;
	hookHandlers.debugPrint 	= arduinoDebugPrintHookHandler;
	
	terminalBuffers.uuid 			= MKS_UUID;
	terminalBuffers.deviceType 		= MKS_DEVICE_TYPE;
	terminalBuffers.deviceName 		= MKS_DEVICE_TYPE_NAME;
	terminalBuffers.uuidLen 		= sizeof(MKS_UUID);
	terminalBuffers.deviceTypeLen 	= sizeof(MKS_DEVICE_TYPE);
	terminalBuffers.deviceNameLen 	= sizeof(MKS_DEVICE_TYPE_NAME);
	
	terminalInit(&terminalBuffers, &hookHandlers);
	signalBuffer = terminalBuffers.rx + sizeof(mks_header);
	/*
	 * System defienition area (DO NOT CHANGE)
	 */
	
	DDRB != (1 << signal_pin) | (1 << debug_pin) | (1 << debug2_pin); // | (1 << debug3_pin);
	setTimerValue(t1_comp);
	
	/*
		Clear OC1A/OC1B on compare match when up-counting. Set
		OC1A/OC1B on compare match when down counting.
		
		Fast PWM, 10-bit (0x03FF)
	 */
	TCCR1A = (1 << COM1A1) | (1 << WGM10) | (1 << WGM12);
	/*
		clkI/O/1 (no prescaling) [PWM period]
	 */
	TCCR1B = (1 << CS10);
	/*
		Enable interrupts.
	 */
	sei();
	/*
		Enable overflow interrupt
	 */
	TIMSK1 = (1 << TOIE1);
	/*
		Set counter compare (duty cycle)
	 */
	OCR1A = 0;
}

uint8_t serialDataLength = 0;
void loop() {
	serialDataLength = Serial.available();	
	if (serialDataLength > 0) {
		/*
		 * System defienition area (DO NOT CHANGE)
		 */
		terminalBuffers.rxLen = Serial.readBytesUntil('\n', terminalBuffers.rx, MAX_LENGTH);
		PORTB = PORTB | (1 << debug_pin);
		dataArrived(&terminalBuffers, &hookHandlers, customOpcodeHandler);
		PORTB = PORTB & (~(1 << debug_pin));
		/*
		 * System defienition area (DO NOT CHANGE)
		 */
	}
	
	if (TRUE == signalGeneratorWorking) {
		PORTB = PORTB | (1 << signal_pin);
		PORTB = PORTB & (~(1 << signal_pin));
	}
}

ISR(TIMER1_OVF_vect) {
	OCR1A = amplitude;
}

int value = 0;
ISR(TIMER0_COMPA_vect) {
	TCNT0 = 0;
		
	if (bufferIndex < bufferSize - 1) {
		amplitude = *(signalBuffer + bufferIndex);
		bufferIndex++;
		PORTB = PORTB | (1 << debug2_pin);
		PORTB = PORTB & (~(1 << debug2_pin));
	} else {
		amplitude = 0;
	}
}

void setTimerValue(uint16_t prescaler) {// Reset TIMER1 values
	TCCR0A 	= 0;
	// Reset TIMER1 counter
	TCNT0 	= 0;
	// Set TIMER1 compare value
	OCR0A 	= prescaler;
}

void startTimer(void) {
	// Enable TIMER1 compare interrupt
	TIMSK0 = (1 << OCIE0A);
	// Enable global interrupts
	sei();
}

void stopTimer(void) {
	// Reset TIMER1 values
	TCCR0A 	= 0;
	// Disable TIMER1 compare interrupt
	TIMSK0 	= 0;
	// Set TIMER1 compare value
	OCR0A 	= 0;
	PORTB = PORTB & (~(1 << signal_pin));
}

void customOpcodeHandler(uint16_t opcode, uint8_t * data) {
	switch (opcode) {
		case OPCODE_SIGNAL_GENERATION_CONFIG: {
			SignalGenerationConfigHeader* header = (SignalGenerationConfigHeader *)&terminalBuffers.rx[sizeof(mks_header)];
		}
		break;
		case OPCODE_SIGNAL_GENERATION_START: {
			startTimer();
			signalGeneratorWorking = TRUE;
		}
		break;
		case OPCODE_SIGNAL_GENERATION_BUFFER: {
			SignalGenerationBufferHeader* header = (SignalGenerationBufferHeader *)&terminalBuffers.rx[sizeof(mks_header)];
			signalBuffer = &(header->buffer);
			bufferSize 	 = header->signalsCount;
			bufferIndex	 = 0;
			Serial.println(bufferSize);
			
			if (!signalGeneratorWorking) {
				startTimer();
				signalGeneratorWorking = TRUE;
			}
		}
		break;
		case OPCODE_SIGNAL_GENERATION_STOP: {
			stopTimer();
			signalGeneratorWorking = FALSE;
		}
		break;
	}
}

/*
 * System defienition area (DO NOT CHANGE)
 */
void
arduinoDebugPrintHookHandler(uint8_t * buffer) { }

void
arduinoTerminalPrintHookHandler(unsigned char * buffer, uint16_t len) {
	Serial.write(buffer, len);
}
/*
 * System defienition area (DO NOT CHANGE)
 */

void blink(void) {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(100);
  digitalWrite(LED_BUILTIN, LOW);
  delay(100);
}
