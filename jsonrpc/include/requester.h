/*
 * requester.h
 *
 *  Created on: 26/08/2008
 *      Author: Michael Lunnay
 */

#ifndef REQUESTER_H_
#define REQUESTER_H_

#include "value.h"
#include "tcpipconnection.h"
#include "methodcall.h"
#include "response.h"

namespace jsonrpc {

	class Requester {
	public:
		Requester(const TCPIPConnection& conn) : mConn(conn) {}

		// make a JSON-RPC call to the server.
		Response call(MethodCall meth, const bool notification = false,
			boost::function<bool (unsigned int, unsigned int)> callback = 0);

		// Convenience method for notifications with no reply.
		// calls call with passed method and notification set to true.
		void notify(const MethodCall& meth,
			boost::function<bool (unsigned int, unsigned int)> callback = 0) {
			call(meth, true, callback);
		}

		const TCPIPConnection getConnection() const { return mConn; }

		void setConnection(const TCPIPConnection& conn) { mConn = conn; }

	private:
		Requester() : mConn("localhost", 0) {}	// no default constructor

		TCPIPConnection mConn;
	};

}

#endif /* REQUESTER_H_ */
