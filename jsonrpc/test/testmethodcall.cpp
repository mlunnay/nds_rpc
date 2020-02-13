#include <iostream>
#include <limits>

#include "../include/methodcall.h"
#include "../include/except.h"

using namespace std;
using namespace jsonrpc;

int main(void) {

	MethodCall call("test");
	call.addParam(Number(5));
	call.addParam(String("foo"));

	cout << call.jsonString() << endl;
	try {
		cout << value_cast<String>(call.getParam(1)).getValue() << endl;
	}
	catch (const exception& e){
		cout << e.what() << endl;
	}

	MethodCall c2("test2");
	c2.addParam("one", Number(5)).addParam("two", String("bar"));

	cout << c2.jsonString(true) << endl;
	cout << value_cast<String>(c2.getParam("two")).getValue() << endl;

	cout << MethodCall("empty").jsonString() << endl;

	return 0;
}
