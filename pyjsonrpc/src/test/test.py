import jsonrpc

class TestService(object):
    _jsonrpcName = "Test"
    def __init__(self):
        pass
    
    @jsonrpc.serviceProcedure(summary="func1 summary")
    def func1(self, arg):
        print 'func1:', arg
    
    def func2(self):
        print 'func2:'
    
    @jsonrpc.serviceProcedure(params=[jsonrpc.Number('one'), jsonrpc.String('two')], ret=jsonrpc.Array())
    def func3(self, one, two):
        """Accepts a number and a string and returns a list of both arguments."""
        
        print one, two
        return [one, two]

@jsonrpc.serviceProcedure("func4", "function 4")
def testFunc1():
    print 'testFunc1: called as func4'

def testFunc2(a, b):
    print 'testFunc2:', a, b
    raise jsonrpc.JSONRPCNotImplementedError("called from registered function")

service = jsonrpc.ServiceHandler('TestService', summary='ServiceHandler test implementation')
service.registerFunction(testFunc1)
service.registerFunction(testFunc2)
service.registerFunction(testFunc2, 'funcTest')
service.registerService(TestService())

print service.listMethods()
import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(service.describe())

print service.handleRequest('{"jsonrpc": "2.0", "method": "system.echo", "params": ["test", 2.2, true], "id": 234}')
print service.handleRequest('{"jsonrpc": "2.0", "method": "Test.func3", "params": [1, "One"], "id": 235}')
print service.handleRequest('{"jsonrpc": "2.0", "method": "funcTest", "params": {"a": 1, "b": 1.1}}')
print service.handleRequest('{"jsonrpc": "2.0"')
print service.handleRequest('{"jsonrpc": "2.0", "method": "badTest", "params": [1], "id": 236}')
print service.handleRequest('"test"')
