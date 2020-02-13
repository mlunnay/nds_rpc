/*
 * response.cpp
 *
 *  Created on: 19/08/2008
 *      Author: Michael Lunnay
 */

#include "../include/response.h"

namespace jsonrpc {

	// set the result with a non error value
	void Response::setResult(const Value& val) {
		mError = false;
		mValue = val;
	}

	// set the response as an error with just an error code and a message
	void Response::setError(const int code, const std::string& message) {
		mError = true;
		Object obj;
		obj["code"] = Number(code);
		obj["message"] = String(message);
		mValue = obj;
	}

	// set the response as an error with an error code, a message and extra data
	void Response::setError(const int code, const std::string& message, const Value& val) {
		mError = true;
		Object obj;
		obj["code"] = Number(code);
		obj["message"] = String(message);
		obj["data"] = val;
		mValue = obj;
	}

}
