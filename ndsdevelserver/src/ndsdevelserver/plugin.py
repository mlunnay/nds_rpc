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

# This is a based apon, and uses some code from Trac (http://trac.edgewall.org)

# Copyright (C) 2003-2008 Edgewall Software
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  3. The name of the author may not be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__all__ = ['Plugin', 'ExtensionPoint', 'implements', 'Interface',
           'PluginError']

class PluginError(Exception):
    """Exception base class for errors in plugins."""
    
    def __init__(self, message, show_traceback=False):
        
        Exception.__init__(self, message)
        self.message = message

        self.show_traceback = show_traceback

    def __unicode__(self):
        return unicode(self.message)

class Interface(object):
    """Marker base class for extension point interfaces."""


class ExtensionPoint(property):
    """Marker class for extension points in plugins."""

    def __init__(self, interface):
        """Create the extension point.
        
        @param interface: the `Interface` subclass that defines the protocol
            for the extension point
        """
        property.__init__(self, self.extensions)
        self.interface = interface
        self.__doc__ = 'List of plugins that implement `%s`' % \
                       self.interface.__name__

    def extensions(self, plugin):
        """Return a list of plugins that declare to implement the extension
        point interface.
        """
        extensions = PluginMeta._registry.get(self.interface, [])
        return filter(None, [plugin.pluginmgr[cls] for cls in extensions])

    def __repr__(self):
        """Return a textual representation of the extension point."""
        return '<ExtensionPoint %s>' % self.interface.__name__


class PluginMeta(type):
    """Meta class for plugins.
    
    Takes care of plugin and extension point registration.
    """
    _plugins = []
    _registry = {}

    def __new__(cls, name, bases, d):
        """Create the plugin class."""

        new_class = type.__new__(cls, name, bases, d)
        if name == 'Plugin':
            # Don't put the Plugin base class in the registry
            return new_class

        # Only override __init__ for Plugins not inheriting PluginManager
        if True not in [issubclass(x, PluginManager) for x in bases]:
            # Allow plugins to have a no-argument initializer so that
            # they don't need to worry about accepting the plugin manager
            # as argument and invoking the super-class initializer
            init = d.get('__init__')
            if not init:
                # Because we're replacing the initializer, we need to make sure
                # that any inherited initializers are also called.
                for init in [b.__init__._original for b in new_class.mro()
                             if issubclass(b, Plugin)
                             and '__init__' in b.__dict__]:
                    break
            def maybe_init(self, plugmgr, init=init, cls=new_class):
                if cls not in plugmgr.plugins:
                    plugmgr.plugins[cls] = self
                    if init:
                        try:
                            init(self)
                        except:
                            del plugmgr.plugins[cls]
                            raise
            maybe_init._original = init
            new_class.__init__ = maybe_init

        if d.get('abstract'):
            # Don't put abstract plugin classes in the registry
            return new_class

        PluginMeta._plugins.append(new_class)
        registry = PluginMeta._registry
        for interface in d.get('_implements', []):
            registry.setdefault(interface, []).append(new_class)
        for base in [base for base in bases if hasattr(base, '_implements')]:
            for interface in base._implements:
                registry.setdefault(interface, []).append(new_class)

        return new_class


class Plugin(object):
    """Base class for plugins.

    Every plugin can declare what extension points it provides, as well as
    what extension points of other plugin it extends.
    """
    __metaclass__ = PluginMeta

    def __new__(cls, *args, **kwargs):
        """Return an existing instance of the plugin if it has already been
        activated, otherwise create a new instance.
        """
        # If this plugin is also the plugin manager, just invoke that
        if issubclass(cls, PluginManager):
            self = super(Plugin, cls).__new__(cls)
            self.plugmgr = self
            return self

        # The normal case where the plugin is not also the plugin manager
        plugmgr = args[0]
        self = plugmgr.plugins.get(cls)
        if self is None:
            self = super(Plugin, cls).__new__(cls)
            self.plugmgr = plugmgr
            plugmgr.plugin_activated(self)
        return self

    def implements(*interfaces):
        """Can be used in the class definiton of `Plugin` subclasses to
        declare the extension points that are extended.
        """
        import sys

        frame = sys._getframe(1)
        locals_ = frame.f_locals

        # Some sanity checks
        assert locals_ is not frame.f_globals and '__module__' in locals_, \
               'implements() can only be used in a class definition'

        locals_.setdefault('_implements', []).extend(interfaces)
    implements = staticmethod(implements)


implements = Plugin.implements

class PluginManager(object):
    """The plugin manager keeps a pool of active plugins."""

    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins = {}
        self.enabled = {}
        if isinstance(self, Plugin):
            self.plugins[self.__class__] = self

    def __contains__(self, cls):
        """Return wether the given class is in the list of active plugins."""
        return cls in self.plugins

    def __getitem__(self, cls):
        """Activate the plugin instance for the given class, or return the
        existing the instance if the plugin has already been activated.
        """
        if cls not in self.enabled:
            self.enabled[cls] = self.is_plugin_enabled(cls)
        if not self.enabled[cls]:
            return None
        plugin = self.plugins.get(cls)
        if not plugin:
            if cls not in PluginMeta._plugins:
                raise PluginError('Plugin "%s" not registered' % cls.__name__)
            try:
                plugin = cls(self)
            except TypeError, e:
                raise PluginError('Unable to instantiate plugin %r (%s)' %
                                (cls, e))
        return plugin

    def plugin_activated(self, plugin):
        """Can be overridden by sub-classes so that special initialization for
        plugins can be provided.
        """

    def is_plugin_enabled(self, cls):
        """Can be overridden by sub-classes to veto the activation of a
        plugin.

        If this method returns False, the plugin with the given class will
        not be available.
        """
        return True
