/*
 * testtcpip.cpp
 *
 *  Created on: 26/08/2008
 *      Author: Michael Lunnay
 */

#include <iostream>
#include <string>
#include <cstring>

#include "../include/tcpipconnection.h"
#include "../include/except.h"

using namespace std;
using namespace jsonrpc;

class callback{
public:
	bool operator()(unsigned int progress, unsigned int total) {
		cout << progress << " " << total << endl;
		if(total) {
			int percent = (progress / (float)total) * 100;
			cout << percent << "% complete of " << total << " bytes." << endl;
		}
		else {
			cout << progress << " bytes downloaded." << endl;
		}
		return true;
	}
};

class falseCallback{
public:
	bool operator()(unsigned int progress, unsigned int total) {
		cout << progress << " " << total << endl;
		if(total) {
			int percent = (progress / (float)total) * 100;
			cout << percent << "% complete of " << total << " bytes." << endl;
		}
		else {
			cout << progress << " bytes downloaded." << endl;
		}
		cout << "canceling operation." << endl;
		return false;
	}
};

int main(void) {
	TCPIPConnection conn("localhost", 50042);
	cout << "this hostname: " << conn.getHostName() << endl;
	cout << "port: " << conn.getPort() << endl;
	cout << "peer hostname: " << conn.getPeerName() << endl;
	cout << "peer address: " << conn.getPeerAddress() << endl;

	string json("{\"jsonrpc\": \"2.0\", \"method\": \"system.echo\", \"params\": [\"test\", 2.2, true], \"id\": 234}");

//	cout << "sending: " << json << endl;
//	conn.write(json);

	string ret = conn.sendRecieve(json);// = conn.read();
	cout << "recieved: " << ret << endl;

	cout << "testing long string" << endl;

	json = "{\"jsonrpc\": \"2.0\", \"method\": \"system.echo\", \"params\": [\"*";
	for(int i = 0; i < 5000; i++) {
		json += "-";
	}
	json += "*\", 2.2, true], \"id\": 234}";

	conn.connect();

//	cout << "sending:  " << json << endl;
	try {
		try {
			conn.write(json, 0, callback());
		} catch (const TransportErrorException& ex) {
			cout << ex.getFullDescription() << endl;
		}

		try {
		 ret = conn.read(0, callback());
		} catch (const TransportErrorException& ex) {
			cout << ex.getFullDescription() << endl;
		}
	} catch(const ActionCanceledException& ex) {
		cout << ex.getDescription() << endl;
	}
//	cout << "recieved: " << ret << endl;

	return 0;
}
