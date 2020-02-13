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

__all__ = ['ServicePluginHandler', 'IRPCService']

from jsonrpc import ServiceHandler, ServiceHolder, niceJSON
from plugin import Plugin, ExtensionPoint, Interface

class IRPCService(Interface):
    """Plugin Interface for Service plugins."""

class ServicePluginHandler(ServiceHandler):
    """This jsonrpc ServiceHandler subclass initializes services from plugins.""" 
    
    service_plugins = ExtensionPoint(IRPCService)
    
    def __init__(self, name, env, id = None, version = None, summary = None,
                 help = None, json = niceJSON(True), sysServices = True):
        ServiceHandler.__init__(self, name, id, version, summary, help, json,
                                sysServices)
        self.env = env
    
    def findServiceEndpoint(self, name):
        """Overrides ServiceHandler.findServiceEndpoint to first check plugins.
        
        If a plugin is not found that matches the service endpoint then the
        base method is called.
        
        """
        
        for plugin in self.service_plugins.extensions(self.env):
            sh = ServiceHolder(plugin)
            if name.startswith(sh.name) and name[len(sh.name)] == '.':
                return sh
        
        return ServiceHandler.findServiceEndpoint(self, name)
    
    def listMethods(self):
        """Overrides ServiceHandler.listMethods to add methods supplied by plugins."""
        
        methods = ServiceHandler.listMethods(self)
        for plugin in self.service_plugins.extensions(self.env):
            methods.extend(ServiceHolder(plugin).listMethods())
        
        return methods
    
    def methodSignature(self, name):
        """Overrides ServiceHandler.methodSignature to return method signatures supplied by plugins."""
        
        for plugin in self.service_plugins.extensions(self.env):
            sh = ServiceHolder(plugin)
            if name.startswith(sh.name) and name[len(sh.name)] == '.':
                return sh.methodSignature(name[len(sh.name)+1:])
        
        return ServiceHandler.methodSignature(self, name)
    
    def methodHelp(self, name):
        """Overrides ServiceHandler.methodHelp to return help on methods supplied by plugins."""
        
        for plugin in self.service_plugins.extensions(self.env):
            sh = ServiceHolder(plugin)
            if name.startswith(sh.name) and name[len(sh.name)] == '.':
                return sh.methodHelp(name[len(sh.name)+1:])
        
        return ServiceHandler.methodHelp(self, name)
    
    def describe(self):
        """Overrides ServiceHandler.describe to return help on methods supplied by plugins."""
        
        obj = ServiceHandler.describe(self)
        procs = obj.setdefault('procs', [])
        for plugin in self.service_plugins.extensions(self.env):
            sh = ServiceHolder(plugin)
            procs.extend(sh.methodDescriptions())
        
        return obj
        
