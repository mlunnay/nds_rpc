/*
 * value.cpp
 *
 *  Created on: 12/08/2008
 *      Author: Michael Lunnay
 */

#include <boost/algorithm/string.hpp>

#include "../include/value.h"
#include "../include/except.h"

namespace jsonrpc {

#define JSONRPC_STRINGIFY(name) #name

#define JSONRPC_ASSERT_VALUE_TYPE(x) \
  if (x != getType() ) { \
	  JSONRPC_EXCEPT(jsonrpc::Exception::ECRTAssertionFailed,\
			  ("Value type mismatch. Expected: " #x\
			  " Actual type: " + ValueTypeNames[getType()]).c_str())\
  }

//const char* ValueTypeNames[] =
std::string ValueTypeNames[] =
  {
  JSONRPC_STRINGIFY( VTNull ),
  JSONRPC_STRINGIFY( VTBool ),
  JSONRPC_STRINGIFY( VTNumber ),
  JSONRPC_STRINGIFY( VTString ),
  JSONRPC_STRINGIFY( VTArray ),
  JSONRPC_STRINGIFY( VTObject )
  };


Value::Value() : mValue(Null::ptr(new Null())) {}

// copy constructor
Value::Value(const Value& val) : mValue(val.mValue) {}

// create a Value from a shared_ptr<ValueBase>
Value::Value(const value_type& val) : mValue(val) {}

// These constructors create a shared pointer to a copy of the value passed
Value::Value(const Null& val) : mValue(value_type(new Null(val))) {}

Value::Value(const Bool& val) : mValue(value_type(new Bool(val))) {}

Value::Value(const Number& val) : mValue(value_type(new Number(val))) {}

Value::Value(const String& val) : mValue(value_type(new String(val))) {}

Value::Value(const Array& val) : mValue(value_type(new Array(val))) {}

Value::Value(const Object& val) : mValue(value_type(new Object(val))) {}

Value& Value::operator=(const Value& rhs) {
	mValue = rhs.mValue;

	return *this;
}

Value& Value::operator=(const value_type& rhs) {
	mValue = rhs;

	return *this;
}

ValueType Value::getType() const { return mValue->getType(); }

bool Value::isType(ValueType val) const { return mValue->isType(val); }

std::string Value::jsonString() const { return mValue->jsonString(); }

std::string Value::typeString() const { return mValue->typeString(); }

// type determination functions
bool Value::isNull() const { return mValue->isType(VTNull); }

bool Value::isBool() const { return mValue->isType(VTBool); }

bool Value::isNumber() const { return mValue->isType(VTNumber); }

bool Value::isString() const { return mValue->isType(VTString); }

bool Value::isArray() const { return mValue->isType(VTArray); }

bool Value::isObject() const { return mValue->isType(VTObject); }

//Value::operator Null&() {
//	JSONRPC_ASSERT_VALUE_TYPE(VTNull);
//	return *(std::tr1::dynamic_pointer_cast<Null>(mValue).get());
//}
//
//Value::operator const Null&() const {
//	JSONRPC_ASSERT_VALUE_TYPE(VTNull);
//	return *(std::tr1::dynamic_pointer_cast<Null>(mValue).get());
//}
//
//Value::operator std::tr1::shared_ptr<Null>() {
//	return std::tr1::dynamic_pointer_cast<Null>(mValue);
//}
//
//Value::operator Bool&() {
//	JSONRPC_ASSERT_VALUE_TYPE(VTBool);
//	return *(std::tr1::dynamic_pointer_cast<Bool>(mValue).get());
//}
//
//Value::operator const Bool&() const {
//	JSONRPC_ASSERT_VALUE_TYPE(VTBool);
//	return *(std::tr1::dynamic_pointer_cast<Bool>(mValue).get());
//}
//
//Value::operator std::tr1::shared_ptr<Bool>() {
//	return std::tr1::dynamic_pointer_cast<Bool>(mValue);
//}
//
//Value::operator Number&() {
//	JSONRPC_ASSERT_VALUE_TYPE(VTNumber);
//	return *(std::tr1::dynamic_pointer_cast<Number>(mValue).get());
//}
//
//Value::operator const Number&() const {
//	JSONRPC_ASSERT_VALUE_TYPE(VTNumber);
//	return *(std::tr1::dynamic_pointer_cast<Number>(mValue).get());
//}
//
//Value::operator std::tr1::shared_ptr<Number>() {
//	return std::tr1::dynamic_pointer_cast<Number>(mValue);
//}
//
//Value::operator String&() {
//	JSONRPC_ASSERT_VALUE_TYPE(VTString);
//	return *(std::tr1::dynamic_pointer_cast<String>(mValue).get());
//}
//
//Value::operator const String&() const {
//	JSONRPC_ASSERT_VALUE_TYPE(VTString);
//	return *(std::tr1::dynamic_pointer_cast<String>(mValue).get());
//}
//
//Value::operator std::tr1::shared_ptr<String>() {
//	return std::tr1::dynamic_pointer_cast<String>(mValue);
//}
//
//Value::operator Array&() {
//	JSONRPC_ASSERT_VALUE_TYPE(VTArray);
//	return *(std::tr1::dynamic_pointer_cast<Array>(mValue).get());
//}
//
//Value::operator const Array&() const {
//	JSONRPC_ASSERT_VALUE_TYPE(VTArray);
//	return *(std::tr1::dynamic_pointer_cast<Array>(mValue).get());
//}
//
//Value::operator std::tr1::shared_ptr<Array>() {
//	return std::tr1::dynamic_pointer_cast<Array>(mValue);
//}
//
//Value::operator Object&() {
//	JSONRPC_ASSERT_VALUE_TYPE(VTObject);
//	return *(std::tr1::dynamic_pointer_cast<Object>(mValue).get());
//}
//
//Value::operator const Object&() const {
//	JSONRPC_ASSERT_VALUE_TYPE(VTObject);
//	return *(std::tr1::dynamic_pointer_cast<Object>(mValue).get());
//}
//
//Value::operator std::tr1::shared_ptr<Object>() {
//	return std::tr1::dynamic_pointer_cast<Object>(mValue);
//}

bool ValueBase::operator==(const ValueBase& other) const {
	if(mType == other.mType)
		return (compare(other) == 0);
	else
		return false;
}

bool ValueBase::operator!=(const ValueBase& other) const {
	if(mType == other.mType)
		return (compare(other) != 0);
	else
		return true;
}

bool ValueBase::operator<(const ValueBase& other) const {
	if(mType == other.mType)
		return (compare(other) == -1);
	else
		return mType < other.mType;
}

int Bool::compare(const ValueBase& other) const {
	bool ovalue = dynamic_cast<const Bool&>(other).mValue;
	if(mValue == ovalue)
		return 0;
	else if(mValue < ovalue)
		return -1;
	else
		return 1;
}

//bool Int::compare(const ValueBase& other) const {
//	return (mValue == dynamic_cast<const Int&>(other).mValue);
//}
//
//bool Double::compare(const ValueBase& other) const {
//	return (mValue == dynamic_cast<const Double&>(other).mValue);
//}

int Number::compare(const ValueBase& other) const {
	double ovalue = dynamic_cast<const Number&>(other).mValue;
	if(mValue == ovalue)
		return 0;
	else if(mValue < ovalue)
		return -1;
	else
		return 1;
}

int String::compare(const ValueBase& other) const {
	std::string ovalue = dynamic_cast<const String&>(other).mValue;
	if(mValue == ovalue)
		return 0;
	else if(mValue < ovalue)
		return -1;
	else
		return 1;
}

// return a copy of the string with all control characters escaped
std::string String::escapeString(const std::string& str) {
	std::string tmp = boost::replace_all_copy(str, "\"", "\\\"");
	boost::replace_all(tmp, "\\", "\\\\");
	boost::replace_all(tmp, "/", "\\/");
	boost::replace_all(tmp, "\b", "\\b");
	boost::replace_all(tmp, "\f", "\\f");
	boost::replace_all(tmp, "\n", "\\n");
	boost::replace_all(tmp, "\r", "\\r");
	boost::replace_all(tmp, "\t", "\\t");

	return tmp;
}

int Array::compare(const ValueBase& other) const {
	if(mValue == dynamic_cast<const Array&>(other).mValue)
		return 0;
	else if(mValue < dynamic_cast<const Array&>(other).mValue)
		return -1;
	else
		return 1;
}

std::string Array::doJsonString() const {
	std::stringstream ss;
	ss << "[";
	bool first = true;
	for(const_iterator it = mValue.begin(); it != mValue.end(); it++) {
		if(!first)
			ss << ", ";
		else
			first = false;
		ss << it->jsonString();
	}
	ss << "]";
	return ss.str();
}

int Object::compare(const ValueBase& other) const {
	if(mValue == dynamic_cast<const Object&>(other).mValue)
		return 0;
	else if(mValue < dynamic_cast<const Object&>(other).mValue)
		return -1;
	else
		return 1;
}

std::string Object::doJsonString() const {
	std::stringstream ss;
	ss << "{";
	bool first = true;
	for(const_iterator it = mValue.begin(); it != mValue.end(); it++) {
		if(!first)
			ss << ", ";
		else
			first = false;
		ss << "\"" << String::escapeString(it->first) << "\"";
		ss << ": " << it->second.jsonString();
	}
	ss << "}";
	return ss.str();
}
// return true if this Object has a given key
bool Object::hasKey(const std::string& key) const {
	const_iterator it = mValue.find(key);
	if(it == mValue.end())
		return false;
	else
		return true;
}

// retrieve the value of key, if key doesn't exist return _default
Object::mapped_type Object::get(const std::string& key, const Object::mapped_type& _default) const {
	const_iterator it = mValue.find(key);
	if(it != mValue.end())
		return it->second;
	else
		return _default;
}

}
