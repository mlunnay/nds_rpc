/*
 * testrequester.cpp
 *
 *  Created on: 26/08/2008
 *      Author: Michael Lunnay
 */

#include <iostream>

#include "../include/requester.h"
#include "../include/value.h"
#include "../include/response.h"
#include "../include/tcpipconnection.h"
#include "../include/methodcall.h"

using namespace std;
using namespace jsonrpc;

int main(void) {
	TCPIPConnection conn("localhost", 50042);
	Requester req(conn);

	MethodCall call("system.echo");
	call.addParam(String("test")).addParam(Number(3.4));
	call.addParam(Bool(true)).addParam(Null());

	try {
		Response ret = req.call(call);

		if(ret.isError()) {
			cout << "req.call returned an error." << endl;
			Object res = value_cast<Object>(ret.getResult());
			cout << "code: " << value_cast<Number>(res["code"]).getValue() << endl;
			cout << "message: " << value_cast<String>(res["message"]).getValue() << endl;
		}
		else {
			cout << "req.call returned a result." << endl;
			cout << ret.getResult().jsonString() << endl;
		}

	} catch(const Exception& e) {
		cout << "Exception: " << e.what() << endl;
	}

	MethodCall listMethods("system.listMethods");

	try {
		Response ret = req.call(listMethods);

		if(ret.isError()) {
			cout << "req.call returned an error." << endl;
			Object res = value_cast<Object>(ret.getResult());
			cout << "code: " << value_cast<Number>(res["code"]).getValue() << endl;
			cout << "message: " << value_cast<String>(res["message"]).getValue() << endl;
		}
		else {
			cout << "Methods provided by server:" << endl;
			if(ret.getResult().isArray()) {
				cout << ret.getResult().jsonString() << endl;
				Array arr = value_cast<Array>(ret.getResult());
				for(Array::iterator it = arr.begin(); it != arr.end(); it++)
					cout << " - " << value_cast<String>(*it).getValue() << endl;
			}
			else {
				cout << "system.listMethod did not return an Array." << endl;
			}
		}

	} catch(const Exception& e) {
		cout << "Exception: " << e.what() << endl;
	}

	return 0;
}
