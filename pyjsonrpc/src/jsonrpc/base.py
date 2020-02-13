# Copyright (c) 2008, Michael Lunnay <mlunnay@gmail.com.au>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Base functionality for jsonrpc"""

from nicefloat import nicefloat
from demjson import JSON, nan, inf, neginf, JSONDecodeError, JSONEncodeError

import inspect
import types
import uuid
import re

from jsonrpcexceptions import *
import parametertypes

__all__ = ['serviceProcedure', 'ServiceHandler', 'ServiceHolder', 'niceJson']

class niceJSON(JSON):
    """A subclass of JSON that uses nicefloat to print the shortest decimal that represents a float."""
    
    def __init__(self, strict=False, compactly=True, escape_unicode=False):
        JSON.__init__(self, strict, compactly, escape_unicode)
    
    def encode_number(self, n):
        if isinstance(n, float):
            global  nan, inf, neginf
            if n is nan:
                return 'NaN'
            elif n is inf:
                return 'Infinity'
            elif n is neginf:
                return '-Infinity'
            
            return nicefloat().str(n)
        else:
            return JSON.encode_number(self, n)

class FunctionMeta(object):
    def __init__(self, name, summary = None, help = None,
                 idempotent = False, params = None, ret = None):
        self.name = name
        self.summary = summary
        self.help = help
        self.idempotent = idempotent
        
        if params:
            if isinstance(params, parametertypes.ParameterBase):
                self.params = [params.getObject()]
            elif isinstance(params, (str, unicode)):
                if params not in parametertypes.parameterStrings:
                    raise InvalidParametersError("Invalid paramater type %s" % params)
                self.params = [params]
            elif isinstance(params, (list, tuple)):
                strList = True
                self.params = []
                for x in params:
                    if isinstance(x, parametertypes.ParameterBase):
                        obj = x.getObject()
                    elif isinstance(x, (str, unicode)):
                        if x not in parametertypes.parameterStrings:
                            raise InvalidParametersError("Invalid paramater type %s" % x)
                        obj = x
                    else:
                        raise InvalidParametersError("Invalid type passed as paramater")
                    
                    if len(self.params) == 0:
                        if isinstance(obj, (str, unicode)):
                            strList = True
                        else:
                            strList = False
                    elif isinstance(obj, (str, unicode)) and strList == False:
                        raise InvalidParametersError("Unnamed parameter added to a named parameter list")
                    elif isinstance(obj, dict) and strList == True:
                        raise InvalidParametersError("Named parameter added to an unnamed parameter list")
                    
                    self.params.append(obj)
                if self.params == []:
                    self.params = None
            else:
                raise InvalidParametersError("Invalid type passed as paramater")     
        else:    
            self.params = None
        
        if ret:
            if isinstance(ret, parametertypes.ParameterBase):
                self.ret = {'type': ret._type}
            elif isinstance(ret, (str, unicode)):
                if ret not in parametertypes.parameterStrings or ret != 'nil':
                    raise InvalidParametersError("Invalid paramater type %s" % ret)
                self.ret = ret
        else:
            self.ret = None  # return value
    
    def description(self, prefix = None):
        """Return a dictionary that represents a JSON-RPC Procedure Description.
        
        if prefix is given it is prepended, followed by a period, to the name.
        
        """
        
        if prefix:
            name = prefix + '.' + self.name
        else:
            name = self.name
        
        obj = {"name": name}
        if self.summary != None:
            obj["summary"] = self.summary
        if self.help != None:
            obj["help"] = self.help
        if self.idempotent == True:
            obj["idempotent"] = True
        if self.params != None:
            obj["params"] = self.params
        if self.ret != None:
            obj["return"] = self.ret
        
        return obj
    
    def signature(self):
        """Return a signature for this function if ret and optionally params hold values, None otherwise."""
        
        if self.params and self.ret:
            sig = [self.ret]
            for p in self.params:
                sig.append(p._type)
            return sig
        elif self.ret:
            return [self.ret]
        else:
            return None

class FunctionHolder(object):
    """A function wrapper for accessing meta data."""
    def __init__(self, function, name = None, summary = None, help = None,
                 idempotent = False, params = None, ret = None):
        self.function = function
        if hasattr(function, '_jsonrpcMeta'):
            self.meta = function._jsonrpcMeta
        else:
            if name == None:
                name = function.__name__
            if help == None:
                help = function.__doc__
            
            self.meta = FunctionMeta(name, summary, help, idempotent, params, ret)
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    
    def name(self):
        return self.meta.name
    
    def help(self):
        return self.meta.help
    
    def params(self):
        return self.mata.params
    
    def ret(self):  # return value
        return self.meta.ret
    
    def description(self, prefix = None):
        return self.meta.description(prefix)
    
    def signature(self):
        return self.meta.signature()

class ServiceHolder(object):
    """A wrapper for accessing services."""
    
    def __init__(self, service, name = None, all = False):
        """ServiceHolder initialization.
        
        if all is true and the service does not provide a relevant introspection method,
        then all class methods not starting with an underscore will be exposed.
        
        """
        
        if name == None:
            if hasattr(service, '_jsonrpcName'):
                self.name = service._jsonrpcName
            else:
                self.name = service.__name__
        else:
            self.name = name
        
        self.service = service
        self.all = all
    
    def listMethods(self, plain = False):
        """Return a list of the methods supplied by this service.
        
        If plain is false (default), return the method names with a prefix of '<service name>.'
        
        """
        
        if hasattr(self.service, '_listMethods'):
            methods = self.service._listMethods()
        elif self.all and not hasattr(self.service, '_dispatch'):
            methods = [x[0] for x in inspect.getmembers(self.service, inspect.ismethod) if not x[0].startswith('_')]
        else:
            methods = [x[1]._jsonrpcMeta.name for x in inspect.getmembers(self.service, inspect.ismethod) if hasattr(x[1], '_jsonrpcMeta')]
        
        if not plain:
            return [self.name + '.' + x for x in methods]
    
    def methodSignature(self, name):
        """Return the method signature of a method."""
        
        if hasattr(self.service, '_methodSignature'):
            return self.service._methodSignature(name)
        elif name in [x[1]._jsonrpcMeta.name for x in inspect.getmembers(self.service, inspect.ismethod) if hasattr(x[1], '_jsonrpcMeta')]:
            return getattr(self.service, name)._jsonrpcMeta.signature()
        else:
            return None
    
    def methodHelp(self, name):
        if hasattr(self.service, '_methodHelp'):
            return self.service._methodHelp(name)
        elif self.all and not hasattr(self.service, '_dispatch') \
            and name in [x[0] for x in inspect.getmembers(self.service, inspect.ismethod) if not x[0].startswith('_')]:
            return getattr(self.service, name).__doc__ or ""
        elif name in [x[1]._jsonrpcMeta.name for x in inspect.getmembers(self.service, inspect.ismethod) if hasattr(x[1], '_jsonrpcMeta')]:
            return getattr(self.service, name)._jsonrpcMeta.summary or ""
        else:
            return ""
    
    def methodDescriptions(self):
        """Return a list of all the method descriptions."""
        
        if hasattr(self.service, '_methodDescriptions'):
            methods = self.service._methodDescriptions()
            for method in methods:
                method['name'] = self.name + '.' + method['name']
        else:
            if self.all and not hasattr(self.service, '_dispatch'):
                methods = []
                for method in [x[1] for x in inspect.getmembers(instance, inspect.ismember()) if not x[0].startswith('_')]:
                    obj = {"name": self.name + '.' + method.__name__}
                    if method.__doc__:
                        obj['summary'] = method.__doc__
                    methods.append(obj)
            else:
                methods = [x[1]._jsonrpcMeta.description(self.name) for x in inspect.getmembers(self.service, inspect.ismethod) if hasattr(x[1], '_jsonrpcMeta')]
        
        return methods
    
    def dispatch(self, name, params = [], kwparams = {}):
        """Attempt to dispatch a call to this instance, passing params.
        
        throws MethodNotFoundError if name is not supplied by this service.
        throws InvalidParametersError if AttributrError is called.
        
        """
        
        if hasattr(self.service, '_dispatch'):
            ret = self.service._dispatch(name, params, kwparams)
        else:
            method = [x[1] for x in inspect.getmembers(self.service, inspect.ismethod) if (hasattr(x[1], '_jsonrpcMeta') and x[1]._jsonrpcMeta.name == name)]
            if method:
                method = method[0]
            else:
                method = [x[1] for x in inspect.getmembers(self.service, inspect.ismethod) if (not x[0].startswith('_') and x[0] == name)]
                if method:
                    method = method[0]
            
            if method:
                try:
                    ret = method(*params, **kwparams)
                except AttributeError, e:
                    raise InvalidParametersError("method %s called with invalid parameters" % name)
            else:
                raise MethodNotFoundError("Method %s not found in service %s" % (name, self.name))
        
        return ret

def serviceProcedure(name = None, summary = None, help = None,
                 idempotent = False, params = None, ret = None):
    """A function decorator that adds JSON-RPC service Procedure information.
    
    Even if its called with no arguments it still requires the call brackets.
    """
    
    def decorate(fn):
        if name == None:
            name_ = fn.__name__
        else:
            name_ = name
        if help == None:
            help_ = fn.__doc__
        else:
            help_ = help
        fn._jsonrpcMeta = FunctionMeta(name_, summary, help_, idempotent, params, ret)
        return fn
    return decorate

_idregex = re.compile('"id"\w*:\w"?(?P<id>.*?)"?\w*,')

class ServiceHandler(object):
    """A JSON-RPC service handler.
    
    similar to SimpleXMLRPCDispatcher, but allows for multiple service instances.
    
    """
    
    def __init__(self, name, id = None, version = None, summary = None,
                 help = None, json = niceJSON(True), sysServices = True):
        self.json = json
        self.functions = {}
        self.services = {}
        
        self.name = name
        # id should really be passed from a stored value.
        if id == None:
           self.id = uuid.uuid4().urn
        elif isinstance(id, uuid.UUID):
            self.id = id.urn 
        else:
            self.id = id
        
        self.version = version
        self.summary = summary
        self.help = help
        
        if sysServices:
            self.registerSystemServices()
    
    def registerService(self, service, name = None, all = None):
        """Register a service instance with this ServiceHandler.
        
        if all is true and the service does not provide a relevant introspection method,
        then all class methods not starting with an underscore will be exposed.
        
        """
        
        # allow the instance to appear under a different name than its class name
        
        sh = ServiceHolder(service, name, all)
        
        if sh.name == 'system':
            raise InvalidParametersError("Attempt made to add reserved system instance.")
        
        self.services[sh.name] = sh
    
    def registerFunction(self, function, name = None, summary = None, help = None,
                         idempotent = False, params = None, ret = None):
        """Register a function to respond to JSON-RPC requests.
        
        The optional arguments are optional values for the service parameter description.
        
        """
        
        fh = FunctionHolder(function, name, summary, help, idempotent, params, ret)
        self.functions[fh.name()] = fh
    
    def registerSystemServices(self):
        """Register the system services functions."""
        
        self.functions['system.listMethods'] = FunctionHolder(self.listMethods, "system.listMethods",
                              "This method returns a list of strings, one for each (non-system) method supported by the JSON-RPC server",
                              ret = parametertypes.Array())
        self.functions['system.methodSignature'] = FunctionHolder(self.methodSignature, "system.methodSignature",
                              "This method takes one parameter, the name of a method implemented by the JSON-RPC server. It returns an array of possible signatures for this method. A signature is an array of types. The first of these types is the return type of the method, the rest are parameters.",
                              params = parametertypes.String(),
                              ret = parametertypes.Array())
        self.functions['system.methodHelp'] = FunctionHolder(self.methodHelp, "system.methodHelp",
                              "This method takes one parameter, the name of a method implemented by the JSON-RPC server. It returns a documentation string describing the use of that method. If no such string is available, an empty string is returned. The documentation string may contain markup.",
                              params = parametertypes.String(),
                              ret = parametertypes.String())
        self.functions['system.echo'] = FunctionHolder(self.echo, "system.echo",
                              'This method takes one parameter of any type, and returns it as "result". It serves as a simple test-function.',
                              params = parametertypes.Any(),
                              ret = parametertypes.Any())
        # possibly support multicall
#===============================================================================
#        self.functions['system.multicall'] = FunctionHolder(self.multicall, "system.multicall",
#                              'Allows the caller to package multiple JSON-RPC calls into a single request. Returning an array of results.',
#                              params = parametertypes.Array(),
#                              ret = parametertypes.Array())
#===============================================================================
    
    def handleRequest(self, json):
        """Handle a method request for this service.
        
        returns a string to be sent,
        or None if the request was a notification and no reply should be sent.
        
        """
        
        err=None
        result = None
        id_=None
        
        try:
            req = self.translateRequest(json)
        except ParseError, e:
            err = e

        if err == None:
            id_ = req.get('id', None)  # if id is None its a notification
            missing = [x for x in ['jsonrpc', 'method'] if not req.has_key(x)]
            if missing:
                err = InvalidRequestError("Required members (%s) missing from request" % ', '.join(missing))
            elif req['jsonrpc'] != '2.0':
                err = InvalidRequestError("service only supports JSON-RPC 2.0")
            else:
                methName = req.get('method')
                args = req.get('params', [])
        
        if err == None:
            try:
                meth = self.findServiceEndpoint(methName)
            except Exception, e:
                err = e
        
        if err == None:
            try:
                result = self.invokeServiceEndpoint(methName, meth, args)
            except JSONRPCError, e:
                err = e
            except Exception, e:
                err = InternalError(str(e))

        if id_ != None:
            resultdata = self.translateResult(result, err, id_)

            return resultdata
        else:
            return None

    def translateRequest(self, data):
        try:
            req = self.json.decode(data)
        except JSONDecodeError, e:
            raise ParseError(str(e))
        return req
     
    def findServiceEndpoint(self, name):
        """Return either a FunctionHolder or ServiceHolder that handles this event.
        
        throws MethodNotFoundError if service is not found.
        
        """
        
        if name == 'service.describe':
            # special case handler for service.describe as it shouldn't describe itself.
            return self.describe
        elif self.functions.has_key(name):
            return self.functions[name]
        else:
            for key in self.services:
                if name.startswith(key) and name[len(key)] == '.':
                    return self.services[key]
            raise MethodNotFoundError(name)

    def invokeServiceEndpoint(self, name, meth, args):
        # first need to determine if args is by value or keyword
        if isinstance(args, list):
            kwargs = {}
        else:
            kwargs = args
            args = []
            
        if isinstance(meth, FunctionHolder):
            return meth(*args, **kwargs)
        else:
            mname = name[len(meth.name)+1:]
            return meth.dispatch(mname, args, kwargs)

    def translateResult(self, rslt, err, id_):
        try:
            obj = {}
            obj["jsonrpc"] = "2.0"
        
            if err != None:
                obj["error"] = err
            else:
                obj["result"] = rslt
            obj["id"] = id_
            
            out = self.json.encode(obj)
        except JSONEncodeError, e:
            out = '{"jsonrpc": "2.0", "error": {"code": -32603, "message": "Internal error.", "data": "Result encoding failed: %s"}, "id": %s}' % (e, self.encoder.encode(id_))

        return out
    
    def listMethods(self):
        """returns a list of strings, one for each (non-system) method supported by this server."""
        
        methods = [x for x in self.functions.keys() if not x.startswith('system.')]
        
        for service in self.services.values():
            methods.extend(service.listMethods())
        
        # just to make sure there arn't any duplicates
        return list(set(methods))
    
    def methodSignature(self, name):
        """Return the method signature of a named function."""
        
        if self.functions.has_key(name):
            return self.functions[name].signature()
        elif name.find('.'):
            for key in self.services:
                if name.startswith(key) and name[len(key)] == '.':
                    return self.services[key].methodSignature(name[len(key)+1:])
        
        return None
    
    def methodHelp(self, name):
        """Return the summary of a method."""
        
        if self.functions.has_key(name):
            return self.functions[name].help()
        elif name.find('.'):
            for key in self.services:
                if name.startswith(key) and name[len(key)] == '.':
                    return self.services[key].methodHelp(name[len(key)+1:])
        
        return ""

    def echo(self, *args, **kwargs):
        """Return the parameters passed."""
        
        if args:
            return args
        else:
            return kwargs

    def describe(self):
        """Return a description object for this JSON-RPC service."""
        
        obj = {'sdversion': '1.0',
            'name': self.name,
            'id': self.id}
        
        if self.version:
            obj['version'] = str(self.version)
        if self.summary:
            obj['summary'] = str(self.summary)
        if self.help:
            obj['help'] = str(self.help)
        
        procs = [x.description() for x in self.functions.values()]
        for x in self.services.values():
            procs.extend(x.methodDescriptions())
        
        if procs:
            obj['procs'] = procs
        
        return obj
