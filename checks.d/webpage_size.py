import sys, gzip, StringIO, urllib2
from checks import AgentCheck


class WebPageSize(AgentCheck):

    def __init__(self, name, init_config, agentConfig, instances=None):
        AgentCheck.__init__(self, name, init_config,
                            agentConfig, instances=instances)

    def check(self, instance):
        value = 0
        name = instance.get('name')
        url = instance.get('url')

        request = urllib2.Request(url)
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request)
        content = response.read()
        response.close()

        fh = StringIO.StringIO(content)
        reply_zipped = gzip.GzipFile(fileobj=StringIO.StringIO(content))

        reply = reply_zipped.read()

        self.gauge('webpage.transferred', round(sys.getsizeof(content) / float(1024), 2), tags=["name:{}".format(name)])
        self.gauge('webpage.characters', len(reply), tags=["name:{}".format(name)])
        self.gauge('webpage.size', round(sys.getsizeof(reply) / float(1024), 2), tags=["name:{}".format(name)])
