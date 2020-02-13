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

__all__ = ['Update']

import os
import zipfile
import hashlib
import time

from yaml import load, dump, YAMLError
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from jsonrpc import serviceProcedure, String, Number, Boolean, Object, Array, ApplicationError, JSONRPCAssertionError
from plugin import Plugin, implements
from filetransfer import IDownloadManipulator
from servicepluginhandler import IRPCService

_VERSION = [1,0]

class Update(Plugin):
    """This is a JSON-RPC service that provides updating functionality."""
    
    _jsonrpcName = "update"
    
    implements(IRPCService, IDownloadManipulator)
    
    #===============================================================================
    # service methods    
    #===============================================================================
    
    @serviceProcedure(summary="returns true if the system supplies a given update, false otherwise.",
                      params=[String('name')],
                      ret=Boolean())
    def hasUpdate(self, name):
        """returns true if the system supplies a given update, false otherwise.
        
        @param name: string containing the name of the update to check.
        @return: True if the system supplies the update, False otherwise.
        
        """
        
        return (self.getUpdateMetadata(name) != None)
    
    @serviceProcedure(summary="Returns the version of the update system.",
                      ret=Array())
    def systemVersion(self):
        """Returns the version of the update system.
        
        @return: An Array containing 2 numbers, the major and minor version
            numbers of the update system.
        
        """
        
        return _VERSION
    
    @serviceProcedure(summary="Returns a string representation of the update systems version.",
                      ret=String())
    def systemVersionString(self):
        """Returns a string representation of the update systems version.
        
        @return: a string representation of the update systems version.
        
        """
        
        return "%d.%d" % tuple(_VERSION)
    
    @serviceProcedure(summary="Returns a string representation of the update systems version.",
                      params=[String('update')],
                      ret=Array())
    def version(self, update):
        """Returns the numeric version of a given update.
        
        @param update: the name of the update.
        @return: An Array containing 2 numbers, with the major and minor version numbers of the update.
        
        """
        
        meta = self.getUpdateMetadata(update)
        if meta == None:
            raise ApplicationError('unknown update %s' % update)
        else:
            return meta['version']
    
    @serviceProcedure(summary="Returns the string representation of the version of a given update.",
                      params=[String('update')],
                      ret=String())
    def versionString(self, update):
        """Returns the string representation of the version of a given update.
        
        @param update: The name of the update.
        @return: A string containing the version of the update.
        
        """
        
        meta = self.getUpdateMetadata(update)
        if meta == None:
            raise ApplicationError('unknown update %s' % update)
        else:
            return '%d.%d' % tuple(meta['version'])\
    
    @serviceProcedure(summary="Returns the meta data of a given update.",
                      params=[String('update')],
                      ret=Object())
    def metaData(self, update):
        """Returns the meta data of a given update.
        
        @param update: The name of the update.
        @return: An Object containging the meta data with the following attributes::
            name: string <package name>,
            version: [major, minor] <update version>,
            timestamp: number <timestamp of update creation>,
            description: string <description>, (optional)
            files: [
              {
                file: string <file name>,
                dlpath: string <download path>,
                path: string <install path>,    (optional default local root directory)
              },
              ...
            ]

        """
        
        meta = self.getUpdateMetadata(update)
        if meta == None:
            raise ApplicationError('unknown update %s' % update)
        
        out = {}
        out['name'] = meta['name']
        out['version'] = meta['version']
        out['timestamp'] = meta['timestamp']
        if meta.had_key('description'):
            out['description'] = meta['description']
        files = []
        
        dlroot = self.config.get('update', {}).get('dlroot', 'update').strip('/')
        
        for f in meta['files']:
            tmp = {}
            tmp['file'] = f['file']
            tmp['dlpath'] = '/%s/%s/%s' % (dlroot, update, f['file'])
            if f.has_key('path'):
                tmp['path'] = f['path']
            files.append(tmp)
        
        out['files'] = files
        
        return out
    
    @serviceProcedure(summary="Returns the creation timestamp of a given update.",
                      params=[String('update')],
                      ret=Number())
    def timestamp(self, update):
        """Returns the creation timestamp of a given update.
        
        @param update: The name of the update
        @return: A float with the updates timestamp in seconds since Epoch (January 1, 1970).
        
        """
        
        meta = self.getUpdateMetadata(update)
        if meta == None:
            raise ApplicationError('unknown update %s' % update)
        
        return meta['timestamp']
    
    @serviceProcedure(summary="Returns the creation timestamp of a given update as an ISO 8601 Format string.",
                      params=[String('update')],
                      ret=String())
    def timestampString(self, update):
        """Returns the creation timestamp of a given update as an ISO 8601 Format string.
        
        @param update: The name of the update.
        @return: The creation timestamp as an ISO Formated string.
        
        """
        
        meta = self.getUpdateMetadata(update)
        if meta == None:
            raise ApplicationError('unknown update %s' % update)
        
        return time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(meta['timestamp']))
    
    @serviceProcedure(summary="Returns the description of a given update.",
                      params=[String('update')],
                      ret=String())
    def description(self, update):
        """Returns the description of a given update.
        
        @param update: The name of the update.
        @return: The updates description or an empty string if no description is given.
        
        """
        
        meta = self.getUpdateMetadata(update)
        if meta == None:
            raise ApplicationError('unknown update %s' % update)
        
        return meta.get('description', '')
    
    @serviceProcedure(summary="Returns an array of file meta data for a given update.",
                      params=[String('update')],
                      ret=Array())
    def files(self, update):
        """Returns an array of file meta data for a given update.
        
        @param update: The name of the update.
        @return: An Array of Objects with members::
            file: string <file name>,
            dlpath: string <download path>,
            path: string <install path>,    (optional default local root directory)
        
        """
        
        meta = self.getUpdateMetadata(update)
        if meta == None:
            raise ApplicationError('unknown update %s' % update)
        
        files = []
        
        dlroot = self.config.get('update', {}).get('dlroot', 'update').strip('/')
        
        for f in meta['files']:
            tmp = {}
            tmp['file'] = f['file']
            tmp['dlpath'] = '/%s/%s/%s' % (dlroot, update, f['file'])
            if f.has_key('path'):
                tmp['path'] = f['path']
            files.append(tmp)
        
        return files
    
    @serviceProcedure(summary="Returns the meta data for file within a given update.",
                      params=[String('update'), String('filename')],
                      ret=Object())
    def fileMetaData(self, update, filename):
        """Returns the meta data for file within a given update.
        
        @param update: The name of the update.
        @param filename: The file to retrieve the meta data for.
        @return: An Objects with members::
            file: string <file name>,
            dlpath: string <download path>,
            path: string <install path>,    (optional default local root directory)
        
        """
        
        meta = self.getUpdateMetadata(update)
        if meta == None:
            raise ApplicationError('unknown update %s' % update)
        
        dlroot = self.config.get('update', {}).get('dlroot', 'update').strip('/')
        
        for f in meta['files']:
            if f['file'] == filename:
                tmp = {}
                tmp['file'] = f['file']
                tmp['dlpath'] = '/%s/%s/%s' % (dlroot, update, f['file'])
                if f.has_key('path'):
                    tmp['path'] = f['path']
                
                return tmp
        else:
            raise ApplicationError('update %s does not contain file %s' % (update, filename))
    
    @serviceProcedure(summary="Returns the install path for a file within a given update.",
                      params=[String('update'), String('filename')],
                      ret=String())
    def filePath(self, update, filename):
        """Returns the install path for a file within a given update.
        
        @param update: The name of the update.
        @param filename: The file to retrieve the meta data for.
        @return: A string containing the install path for the file.
        
        """
        
        meta = self.getUpdateMetadata(update)
        if meta == None:
            raise ApplicationError('unknown update %s' % update)
        
        for f in meta['files']:
            if f['file'] == filename:
                path = ''
                if f.has_key('path'):
                    path = f['path']
                
                return path
        else:
            raise ApplicationError('update %s does not contain file %s' % (update, filename))

    #===============================================================================
    # IDownloadManipulator Methods    
    #===============================================================================
    
    def download(self, head, tail, rootpath):
        """Fetch the data to be sent.
        
        This should return a string with the data to be returned.
        
        @param head: A string with the requested path that precedes tail.
        @param tail: the requested path relative to rootpath.
        @param rootpath: A string with the local rootpath for the path of the request. 
        """
        
        tail_ = tail.lstrip('/')
        tmp = tail_.split('/')
        update = tmp[0]
        path = '/'.join(tmp[1:])
        
        meta = self.getUpdateMetadata(update)
        if meta == None:
            raise ApplicationError('unknown update %s' % update)
        
        for f in meta['files']:
            if f['file'] == path:
                file_meta = f
        else:
            raise IOError('File %s is missing from update %s' % (path, meta['name']))
        
        # is this a file system based update
        if meta['is_dir'] == True:
            data = open(os.path.join(meta['path'], path)).read()
        else:   # the update is an archive
            arch = zipfile.ZipFile(meta['path'], 'r', zipfile.ZIP_DEFLATED)
            data = arch.read(path)
        
        hash = hashlib.sha1()
        hash.update(data)
        
        if file_meta['hash'] != hash.hexdigest():
            self.log.debug('file (%s) sha1 hash does not match update configuration.' % path)
            raise ApplicationError('file (%s) sha1 hash does not match update configuration.' % path)
        
        return data 
    
    def handles(self, head, tail):
        """Utility method to tell if the plugin handles a particular request.
        
        This will allow a plugin to only handle graphic files by only returning
        true if the file extension is .jpg, .png, etc.
        
        @param head: A string with the requested path that precedes tail.
        @param tail: the requested path relative to rootpath.
        @return: True if this plugin will handle the request, False otherwise. 
        """
        
        return True # we handle all requests
    
    #===============================================================================
    # Utility Methods
    #===============================================================================
    
    def getUpdateMetadata(self, update):
        """This method returns the metadata for an update.
        
        @param update: string containing the name of the update to fetch the metadata for.
        @return: a dictionary containing Update metadata, if the update exists
            and is enabled, None otherwise.
        
        """
        
        path = ''
        
        for update_cfg in self.config.get('update', {}).get('updates', {}):
            if update_cfg['name'] == update:
                if not update_cfg.get('enabled', True):
                    return None
                
                path = update_cfg['path']
                if not os.path.exists(path):
                    return None
                break
        else:
            root = self.config.get('update', {}).get('rootpath', 'updates')
            for i in os.listdir(root):
                if i == update:
                    path = os.path.join(root, i)
                    break
            else:
                return None
        
        # have a path to a possible update, first check if its a file system update
        # or an archive update
        if os.path.isdir(path):
            update_path = os.path.join(path, 'update')
            if not os.path.exists(update_path):
                self.log.debug('update %s does not have an update configuration file' % update)
                return None
            try:
                update_meta = load(open(filename), Loader=Loader)
            except:
                # the CLoader has problems with throwing exceptions so call the python version here to get a meaningful exception
                try:
                    load(open(filename))
                except YAMLError, e:
                    self.log.debug('update %s has invalid configuration file: %s' % (update, str(e)))
                    return None
            update_meta['is_dir'] = True
        else:
            is_dir = False
            if not os.path.splitext(path) == '.dsu' or not zipfile.is_zipfile(path) :
                self.log.debug('update %s is not a valid update archive' % update)
                return None
            
            arch = zipfile.ZipFile(path, 'r', zipfile.ZIP_DEFLATED)
            
            try:
                update_meta = load(arch, Loader=Loader)
            except:
                # the CLoader has problems with throwing exceptions so call the python version here to get a meaningful exception
                try:
                    load(arch)
                except YAMLError, e:
                    self.log.debug('update %s has invalid configuration file: %s' % (update, str(e)))
                    return None
            update_meta['is_dir'] = False
        
        # verify the metadata has the correct version and keys    
        if update_meta.get('dsupdate', [0,0]) != [1,0]:
            self.log.debug('update %s version is not [1,0]' % update)
            return None
        for key in ['name', 'version', 'timestamp', 'files']:
            if not update_meta.has_key(key):
                self.log.debug('update %s has invalid configuration file, missing required key: %s' % (update, key))
                return None
        
        update_meta['path'] = path
        
        # return the metadata
        return update_meta
    
    def file_is_valid(self, meta, path):
        """Test if file_name's sha1 hash matches that in the update's metadata.
        
        @param meta: the updates metadata.
        @param path: the path of the file to check, relative to the update.
        @return: True if the hashes match, False otherwise.
        
        """
        
        for f in meta['files']:
            if f['file'] == path:
                file_meta = f
        else:
            raise IOError('File %s is missing from update %s' % (path, meta['name']))
        
        # is this a file system based update
        if meta['is_dir'] == True:
            data = open(os.path.join(meta['path'], path)).read()
        else:   # the update is an archive
            arch = zipfile.ZipFile(meta['path'], 'r', zipfile.ZIP_DEFLATED)
            data = arch.read(path)
        
        hash = hashlib.sha1()
        hash.update(data)
        
        return (file_meta['hash'] == hash.hexdigest())        
