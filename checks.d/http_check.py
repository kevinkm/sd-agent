from checks.services_checks import ServicesCheck, Status, EventType
from util import headers
import socket
import time
from checks.libs.httplib2 import Http, HttpLib2Error

class HTTPCheck(ServicesCheck):

    def _load_conf(self, instance):
        # Fetches the conf
        username = instance.get('username', None)
        password = instance.get('password', None)
        timeout = int(instance.get('timeout', 10))
        url = instance.get('url', None)
        if url is None:
            raise Exception("Bad configuration. You must specify a url")
        return url, username, password, timeout

    def _check(self, instance):
        addr, username, password, timeout = self._load_conf(instance)
        try:
            self.log.debug("Connecting to %s" % addr)
            h = Http(timeout=timeout, disable_ssl_certificate_validation=True)
            if username is not None and password is not None:
                h.add_credentials(username, password)
            resp, content = h.request(addr, "GET")

        except socket.timeout, e:
            self.log.info("%s is DOWN, error: %s" % (addr, str(e)))
            return Status.DOWN, str(e)

        except HttpLib2Error, e:
            self.log.info("%s is DOWN, error: %s" % (addr, str(e)))
            return Status.DOWN, str(e)

        except socket.error, e:
            self.log.info("%s is DOWN, error: %s" % (addr, repr(e)))
            return Status.DOWN, "Socket error: %s" % repr(e)

        except Exception, e:
            self.log.error("Unhandled exception %s" % str(e))
            raise

        if int(resp.status) >= 400:
            self.log.info("%s is DOWN, error code: %s" % (addr, str(resp.status)))
            return Status.DOWN, str(resp.status)

        self.log.info("%s is UP" % addr)
        return Status.UP, "UP"

    def _create_status_event(self, status, msg, instance):
        # Get the instance settings
        url = instance.get('url', None)
        name = instance.get('name', None)
        
        
        # Get a custom message that will be displayed in the event
        custom_message = instance.get('message', "")
        if custom_message:
            custom_message += " \n"

        # Let the possibility to override the source type name
        instance_source_type_name = instance.get('source_type', None)
        if instance_source_type_name is None:
            source_type = "%s.%s" % (ServicesCheck.SOURCE_TYPE_NAME, name)
        else:
            source_type = "%s.%s" % (ServicesCheck.SOURCE_TYPE_NAME, instance_source_type_name)
        

        # Get the handles you want to notify
        notify = instance.get('notify', self.init_config.get('notify', []))
        notify_message = ""
        if notify:
            notify_list = []
            for handle in notify:
                notify_list.append("@%s" % handle.strip())
            notify_message = " ".join(notify_list) + " \n"

        if status == Status.DOWN:
            title = "[Alert] %s is down" % name
            alert_type = "error"
            msg = "%s %s %s reported that %s (%s) failed with %s" % (notify_message,
                custom_message, self.hostname, name, url, msg)
            event_type = EventType.DOWN

        else: # Status is UP
            title = "[Recovered] %s is up" % name
            alert_type = "success"
            msg = "%s %s %s reported that %s (%s) recovered" % (notify_message,
                custom_message, self.hostname, name,url)
            event_type = EventType.UP

        return {
             'timestamp': int(time.time()),
             'event_type': event_type,
             'host': self.hostname,
             'api_key': self.agentConfig['api_key'],
             'msg_text': msg,
             'msg_title': title,
             'alert_type': alert_type,
             "source_type_name": source_type,
             "event_object": name,
        }


