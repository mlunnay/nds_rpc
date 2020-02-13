#include <iostream>
#include <limits>

#include "../include/value.h"
#include "../include/except.h"

using namespace std;
using namespace jsonrpc;

int main(void) {
	Object dict;
	Array::ptr arr(new Array());
	arr->push_back(Number(5));
	arr->push_back(Bool(true));
	arr->push_back(Null());
	arr->push_back(Number(1.237));
	dict["test"] = arr;
	dict["second"] = String("string");
	dict["third"] = Number::ptr(new Number(24.78));

	cout << dict.jsonString() << endl;

	cout << "- value_casts -" << endl;

	Number vcn = value_cast<Number>((*arr)[0]);
	cout << vcn.getValue() << endl;
	try {
		Bool vcb = value_cast<Bool>((*arr)[0]);
		cout << vcb.getValue() << endl;
	} catch (const BadCastException& ex) {
		cout << "exception caught while trying to value_cast to bool:" << endl;
		cout << ex.getFullDescription() << endl;
	}
	Bool vcc = value_cast<Bool>((*arr)[1]);
	cout << vcc.getValue() << endl;

	Array vca = value_cast<Array>(dict["test"]);

	cout << vca.size() << endl;
	Number::ptr vcn2 = value_cast<Number::ptr>(vca[0]);

	cout << vcn2->getValue() << endl;

	Number::ptr vcn3 = value_cast<Number::ptr>(dict["second"]);
	if(vcn3.get() == 0)
		cout << "dict[\"second\"] is not a number" << endl;
	else
		cout << "dict[\"second\"] is a number" << endl;

	cout << "hasKey(second): " << dict.hasKey("second") << endl;

	Value obj = dict.get("undef", Value(Array()));
	cout << "obj is array: " << obj.isArray() << endl;
	vca = value_cast<Array>(obj);
	cout << "vca size: " << vca.size() << endl;

	cout << (dict["second"] == String("string")) << endl;

	return 0;
}
