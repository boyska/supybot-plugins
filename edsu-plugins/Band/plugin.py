"""
Get a band name from Dan's band name list:
"""

import supybot

__revision__ = "$Id$"
__author__ = supybot.authors.unknown
__contributors__ = {}


import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks

from urllib import urlencode
from urllib2 import urlopen 
from sgmllib import SGMLParser
from random import choice
from os.path import join, dirname, abspath
import simplejson

def configure(advanced):
    # This will be called by setup.py to configure this module.  Advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Band', True)


conf.registerPlugin('Band')
# This is where your configuration variables (if any) should go.

class Parser ( SGMLParser ): 

    inside = False
    bands = []

    def start_pre(self, attrs):
        self.inside = True

    def end_span(self):
        self.inside = False

    def handle_data(self,data):
        if self.inside:
            bands = data.split("\n")
            for band in bands: 
                self.bands.append(band)

class Band(callbacks.Privmsg):

    def oldband(self,irc,msg,args):
        """ 
        Get a band name from dchud's list: http://www-personal.umich.edu/~dchud/fng/names.html
        """

        url = urlopen("http://www-personal.umich.edu/~dchud/fng/names.html")
        html = url.read()

        parser = Parser()
        parser.feed(html)

        band = parser.bands[randint(0,len(parser.bands)-1)]
        irc.reply(band)

    def band(self, irc, msg, args):
        """[add|remove|search {BAND}]
        KA-RAAAAY-ZEE band names!  Get one, add one, remove one, search!
        """
        # this method is ugly as hell, I know
        #f = join(dirname(abspath(__file__)), 'bands.json')
        f = conf.supybot.directories.data.dirize('Band.json')
        try:
            jsonfile = open(f, 'r')
            json = simplejson.load(jsonfile)
            jsonfile.close()
        except IOError, e:
            self.log.warning(str(e))
            json = {'bands': []}
        if len(args) > 1:
            if args[0] == 'add':
                new_band = u' '.join([arg.decode('utf8') for arg in args[1:]]).strip()
                json['bands'].append(new_band)
                try:
                    jsonfile = open(f, 'w')
                    simplejson.dump(json, jsonfile, indent=2)
                    jsonfile.close()
                except IOError, e:
                    self.log.warning(str(e))
                    irc.reply(u"Band '%s' NOT added to list" % new_band, prefixNick=True)
                else:
                    irc.reply(u"Band '%s' added to list" % new_band, prefixNick=True)
            elif args[0] == 'remove':
                band = u' '.join([arg.decode('utf8') for arg in args[1:]]).strip()
                try:
                    json['bands'].remove(band)
                except ValueError:
                    irc.reply("Band '%s' is not in the list" % band, prefixNick=True)
                    return
                try:
                    jsonfile = open(f, 'w')
                    simplejson.dump(json, jsonfile, indent=2)
                    jsonfile.close()
                except IOError, e:
                    self.log.warning(str(e))
                    irc.reply("Band '%s' NOT removed from list" % band, prefixNick=True)
                else:
                    irc.reply("Band '%s' removed from list" % band, prefixNick=True)
            elif args[0] == 'search':
                search_str = u' '.join([arg.decode('utf8') for arg in args[1:]]).strip()
                bands = [band for band in json['bands'] if band.lower().find(search_str.lower()) != -1]
                if bands:
                    band_str = u' ; '.join(bands)
                    irc.reply(band_str.encode('utf8', 'ignore'), prefixNick=True)
                else:
                    irc.reply("No bands found matching '%s'" % search_str.encode('utf8', 'ignore'), prefixNick=True)
        else:
            try:
                band = choice(json['bands'])
            except IndexError:
                band = 'No bands found'
            irc.reply(band, prefixNick=True)

Class = Band 

# vim:set shiftwidth=4 tabstop=8 expandtab textwidth=78:
