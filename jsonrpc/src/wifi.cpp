
#include "../include/wifi.h"
#include <cstring>

//the following stuff depends on a wifi-enabled arm7 core running:

int send( int socket, const char * data ) {
	return send( socket, data, strlen( data ), 0 );
}

//wifi timer function, to update internals of sgIP
void wifi_timer_50ms() {
	Wifi_Timer( 50 );
}

//notification function to send fifo message to arm7
void arm9_synctoarm7() {
	REG_IPC_FIFO_TX=0x87654321;
}

//interrupt handler to receive fifo messages from arm7
void arm9_fifo() {
	if( REG_IPC_FIFO_RX == 0x87654321 ) Wifi_Sync();
}

void init_wifi() {
	REG_IPC_FIFO_CR = IPC_FIFO_ENABLE | IPC_FIFO_SEND_CLEAR; // enable & clear FIFO

	u32 Wifi_pass = Wifi_Init( WIFIINIT_OPTION_USELED );
   	REG_IPC_FIFO_TX = 0x12345678;
   	REG_IPC_FIFO_TX = Wifi_pass;

	*((volatile u16 *)0x0400010E) = 0; // disable timer3

	irqSet( IRQ_TIMER3, wifi_timer_50ms ); // setup timer IRQ
	irqEnable( IRQ_TIMER3 );
   	irqSet( IRQ_FIFO_NOT_EMPTY, arm9_fifo ); // setup fifo IRQ
   	irqEnable( IRQ_FIFO_NOT_EMPTY );

   	REG_IPC_FIFO_CR = IPC_FIFO_ENABLE | IPC_FIFO_RECV_IRQ; // enable FIFO IRQ

   	Wifi_SetSyncHandler( arm9_synctoarm7 ); // tell wifi lib to use our handler to notify arm7

	// set timer3
	*((volatile u16 *)0x0400010C) = -6553; // 6553.1 * 256 cycles = ~50ms;
	*((volatile u16 *)0x0400010E) = 0x00C2; // enable, irq, 1/256 clock

	while( !Wifi_CheckInit() ) { // wait for arm7 to be initted successfully
		swiWaitForVBlank();
	}
}

bool autoconnect_wifi(boost::function<bool (int)> callback) {
	Wifi_AutoConnect();
	while( true ) {
		int i = Wifi_AssocStatus();
		if( i == ASSOCSTATUS_ASSOCIATED ) {
			return true;
		}
		if( i == ASSOCSTATUS_CANNOTCONNECT ) {
			return false;
		}
		if(callback) {
			if(!callback(i)) {
				return false;
			}
		}
	}
}

bool connect_wifi(Wifi_AccessPoint * apdata, int wepmode, int wepkeyid,
		unsigned char * wepkey, boost::function<bool (int)> callback) {
	Wifi_ConnectAP(apdata, wepmode, wepkeyid, wepkey);
	while(true) {
		int i = Wifi_AssocStatus();
		if( i == ASSOCSTATUS_ASSOCIATED ) {
			return true;
		}
		if( i == ASSOCSTATUS_CANNOTCONNECT ) {
			return false;
		}

		if(callback) {
			if(!callback(i)) {
				Wifi_DisconnectAP();
				return false;
			}
		}
	}

}

bool init_socket( int * sock, char * host, int port, bool blocking ) {
	struct sockaddr_in servaddr;
	if( ( *sock = socket( AF_INET, SOCK_STREAM, 0 ) ) < 0 ) {
		return false;
	}

	memset( &servaddr, 0, sizeof( servaddr ) );
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons( port );

	if( !inet_aton( host, &servaddr.sin_addr ) ) {
		servaddr.sin_addr.s_addr = *(unsigned long *) gethostbyname( host )->h_addr_list[0];
	}

	if( blocking ) {
		if( !connect( *sock, (struct sockaddr *) &servaddr, sizeof( servaddr ) ) ) {
			return true;
		}
	} else {
		if( !connect( *sock, (struct sockaddr *) &servaddr, sizeof( servaddr ) ) ) {
			int i = 1;
			ioctl( *sock, FIONBIO, &i );
			return true;
		}
	}

	return false;
}
