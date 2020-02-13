/*
 * requestor.cpp
 *
 *  Created on: 26/08/2008
 *      Author: Michael Lunnay
 */

#include "../include/requester.h"
#include "../include/parse.h"
#include "../include/except.h"

namespace jsonrpc {

	// make a JSON-RPC call to the server.
	Response Requester::call(MethodCall meth, const bool notification,
		boost::function<bool (unsigned int, unsigned int)> callback) {
		mConn.connect();
		mConn.write(meth.jsonString(notification));
		std::string ret = mConn.read(0, callback);
		mConn.disconnect();

//		std::string ret = "{\"id\":234,\"jsonrpc\":\"2.0\",\"result\":[\"test\",2.2,true]}";

		if(ret.empty())
			JSONRPC_EXCEPT(-32700, "Server returned an empty response.")

		Object json;
		try {
			json = value_cast<Object>(parse(ret.begin(), ret.end()));
		} catch (const BadCastException& ex) {
			JSONRPC_EXCEPT(-32700, "Server return value is not a JSON Object.")
		}

		if(!(json.hasKey("jsonrpc") && json["jsonrpc"] == String("2.0"))) {
			JSONRPC_EXCEPT(-32700, "Server return value has missing or wrong jsonrpc version.")
		}

		if(!(json.hasKey("id") && json["id"] == Number(meth.getId()))) {
			JSONRPC_EXCEPT(-32700, "Return id value does not match requests id.")
		}

		Response response;
		if(json.hasKey("result") && json.hasKey("error")) {
			JSONRPC_EXCEPT(-32700, "Server response has both result and error members.")
		}
		else if(json.hasKey("result")) {
			response.setResult(json["result"]);
		}
		else if(json.hasKey("error")) {
			response.setError(json["error"]);
		}
		else {
			JSONRPC_EXCEPT(-32700, "Server response has neither result or error members.")
		}

		return response;
	}

}
