/*
 * methodcall.cpp
 *
 *  Created on: 19/08/2008
 *      Author: Michael Lunnay
 */

#include "../include/methodcall.h"
#include "../include/except.h"

namespace jsonrpc {

	int MethodCall::NextMethodId = 0;

	// return the json string that represents this method call
	// throws a RuntimeAssertionException if mName is empty
	std::string MethodCall::jsonString(const bool notification) const {
		JSONRPC_ASSERT(!mName.empty(), "Method name not set in MethodCall::jsonString()")

		Object method;
		method["jsonrpc"] = String("2.0");
		method["method"] = String(mName);
		if(size() != 0)
			method["params"] = mParams;
		if(!notification)
			method["id"] = Number(mId);

		return method.jsonString();
	}

	// return true if parameters are given by name
	bool MethodCall::namedParams() const {
		return mParams.isType(VTObject);
	}

	// return true if parameters are given by position
	bool MethodCall::positionalParams() const {
		return mParams.isType(VTArray);
	}

	// clear the parameter list
	void MethodCall::clear() {
		mParams = Array();
	}

	// return the number of parameters
	int MethodCall::size() const {
		if(mParams.isType(VTArray)) {
			Array::ptr a = value_cast<Array::ptr>(mParams);
			return a->size();
		}
		else {
			Object::ptr o = value_cast<Object::ptr>(mParams);
			return o->size();
		}
	}

	// add a parameter to the parameter list
	// throws a RuntimeAssertionException if the parameter type is a non empty Object
	MethodCall& MethodCall::addParam(const Value& val) {
		if(mParams.isType(VTObject)) {
			Object::ptr o = value_cast<Object::ptr>(mParams);
			if(o->size() != 0)
				JSONRPC_EXCEPT(jsonrpc::Exception::ECRTAssertionFailed, "Attempted to add non named parameter to named parameter method")

			mParams = Array();
		}
		value_cast<Array::ptr>(mParams)->push_back(val);

		return *this;
	}

	// adds a named parameter to the parameter list
	// throws a RuntimeAssertionException if the parameter type is a non empty Array
	MethodCall& MethodCall::addParam(const std::string& name, const Value& val) {
		if(mParams.isType(VTArray)) {
			Array::ptr o = value_cast<Array::ptr>(mParams);
			if(o->size() != 0)
				JSONRPC_EXCEPT(jsonrpc::Exception::ECRTAssertionFailed, "Attempted to add named parameter to parameter list method")

			mParams = Object();
		}
		(*value_cast<Object::ptr>(mParams))[name] = val;

		return *this;
	}

	// clears the parameter list and sets its first value
	MethodCall& MethodCall::setParam(const Value& val) {
		Array::ptr arr = Array::ptr(new Array());
		arr->push_back(val);
		mParams = arr;

		return *this;
	}

	// clears the parameter list and sets its first named value
	MethodCall& MethodCall::setParam(const std::string& name, const Value& val) {
		Object::ptr obj = Object::ptr(new Object());
		(*obj)[name] = val;
		mParams = obj;

		return *this;
	}

	// returns the parameter at index
	// returns an empty Value if the parameter list is an Object
	Value MethodCall::getParam(const int index) {
		if(mParams.isType(VTObject))
			return Value();

		return (*value_cast<Array::ptr>(mParams))[index];
	}

	// returns the parameter for the given key
	// returns an empty Value if the parameter list is an array or the key does not exist
	Value MethodCall::getParam(const std::string& name) {
		if(mParams.isType(VTArray))
			return Value();

		return (*value_cast<Object::ptr>(mParams))[name];
	}

}  // namespace jsonrpc
