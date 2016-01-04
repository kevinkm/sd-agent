import sys
import urllib2
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

        self.gauge('webpage.kb', round(sys.getsizeof(content) / float(1024), 2), tags=["name:{}".format(name)])
