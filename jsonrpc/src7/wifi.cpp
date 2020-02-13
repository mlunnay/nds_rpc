
#include <nds.h>
#include <dswifi7.h>
#include "../include/wifi.h"

void arm7_synctoarm9() {
	REG_IPC_FIFO_TX = 0x87654321;
}

//interrupt handler to allow incoming notifications from arm9, including wifi init request
void arm7_fifo() {
	u32 msg = REG_IPC_FIFO_RX;

	if( msg == 0x12345678 ) {
		irqDisable( IRQ_FIFO_NOT_EMPTY );
		while( REG_IPC_FIFO_CR & IPC_FIFO_RECV_EMPTY ) {
			swiWaitForVBlank();
		}
		Wifi_Init( REG_IPC_FIFO_RX );
		Wifi_SetSyncHandler( arm7_synctoarm9 ); //allow wifi lib to notify arm9
		irqEnable( IRQ_FIFO_NOT_EMPTY );
	} else if( msg == 0x87654321 ) {
		Wifi_Sync();
	}
}

void dl_init_wifi() {
	irqSet( IRQ_WIFI, Wifi_Interrupt );
	irqEnable( IRQ_WIFI );

	//set up FIFO for wifi init and whatnot
	irqSet( IRQ_FIFO_NOT_EMPTY, arm7_fifo );
	irqEnable( IRQ_FIFO_NOT_EMPTY );
	REG_IPC_FIFO_CR = IPC_FIFO_ENABLE | IPC_FIFO_SEND_CLEAR | IPC_FIFO_RECV_IRQ;
}

