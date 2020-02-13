#include <iostream>
#include <sstream>

#include "../include/parse.h"
#include "../include/except.h"

using namespace std;
using namespace jsonrpc;

std::string valueToString(const Value& val) {
	stringstream ss;
	if(val.isType(VTNull))
		ss << "null";
	else if(val.isType(VTBool)) {
		ss << boolalpha << value_cast<Bool>(val).getValue();
	}
	else if(val.isType(VTNumber)) {
		ss << value_cast<Number>(val).getValue();
	}
	else if(val.isType(VTString)) {
		ss << value_cast<String>(val).getValue();
	}
	return ss.str();
}

int main(void) {
	string jstr = "{ \"Hello\" : [ \"abc\", 1, 2.5, true, false, null ] }";

	try {
		Value val = parse(jstr.begin(), jstr.end());

		cout << "val type: " << val.typeString() << endl;
		Object obj = value_cast<Object>(val);
		cout << "val size: " << obj.size() << endl;

		cout << "key: " << obj.begin()->first << endl;
		cout << "value type: " << obj.begin()->second.typeString() << endl;

		cout << "value members: " << endl;
		Array arr = value_cast<Array>(obj.begin()->second);
		for(Array::iterator it = arr.begin(); it != arr.end(); it++) {
			cout << valueToString(*it) << " ";
		}
		cout << endl;
	}
	catch (const ParseErrorException& e) {
		cout << "unable to parse json string" << endl;
		cout << e.getFullDescription() << endl;
	}

	try {
		jstr = "hello";
		Value val = parse(jstr.begin(), jstr.end());
	}
	catch (const ParseErrorException& e) {
		cout << "unable to parse json string" << endl;
		cout << e.getFullDescription() << endl;
	}

	return 0;
}
