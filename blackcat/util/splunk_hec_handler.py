# Modified/stripped down version of https://github.com/vavarachen/splunk_hec_handler
# Licensed under MIT  https://github.com/vavarachen/splunk_hec_handler/blob/master/LICENCE
import json
import logging
import socket
import time

import requests


class SplunkHecHandler(logging.Handler):
    """
    This module returns a python logging handler capable of sending log records to a Splunk HTTP Event Collector
    listener.  Log records can be simple string or dictionary.  In the latter case, if the sourcetype is configured
    to be _json (or variant), JSON format of the log message will be preserved.

    Example:
        import logging
        from splunk_hec_handler import SplunkHecHandler
        logger = logging.getLogger('SplunkHecHandlerExample')
        logger.setLevel(logging.DEBUG)
        # If using self-signed certificate, set ssl_verify to False
        # If using http, set proto to http
        splunk_handler = SplunkHecHandler('splunkfw.domain.tld',
                            'EA33046C-6FEC-4DC0-AC66-4326E58B54C3',
                            port=8888, proto='https', ssl_verify=True,
                            source="HEC_example")
        logger.addHandler(splunk_handler)
        '''
        Following should result in a Splunk entry with _time set to current timestamp.
            { log_level: INFO
              message: Testing Splunk HEC Info message
            }
        '''
        logger.info("Testing Splunk HEC Info message")

        '''
        Following should result in a Splunk entry with _time of Monday, August 6, 2018 4:33:43 AM, and contain two
        custom fields (color, api_endpoint). Custom fields can be seen in verbose mode.
            { app: my demo
              error codes: [
                1
                23
                34
                456
                ]
            log_level: ERROR
            severity: low
            user: foobar
            }
        '''
        # See http://dev.splunk.com/view/event-collector/SP-CAAAE6P for 'fields'
        # To use fields, sourcetype must be specified and must allow for indexed field extractions
        dict_obj = {'time': 1533530023, 'fields': {'color': 'yellow', 'api_endpoint': '/results'},
                    'user': 'foobar', 'app': 'my demo', 'severity': 'low', 'error codes': [1, 23, 34, 456]}
        logger.error(dict_obj)

    Splunk remote logging configuration
    http://docs.splunk.com/Documentation/SplunkCloud/latest/Data/UsetheHTTPEventCollector
    http://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector
    """
    URL_PATTERN = "{0}://{1}:{2}/services/collector/{3}"
    TIMEOUT = 2

    def __init__(self, host, token, **kwargs):
        """
        Creates a python logging handler, capable of sending logs to Splunk server
        :param host: Splunk server hostname or IP
        :param token: Splunk HEC Token
        (http://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector#About_Event_Collector_tokens)
        :param **kwargs:
            See below

        :keyword Arguments:
            port: 0-65535 port number of Splunk HEC listener
            proto: http | https
            ssl_verify: True|False|Path to cert.  True by default.
                see https://2.python-requests.org/en/master/user/advanced/#ssl-cert-verification
            source: Override source value specified in Splunk HEC configuration.  None by default.
            sourcetype: Override sourcetype value specified in Splunk HEC configuration.  None by default.
            hostname: Specify custom host value.  Defaults to hostname returned by socket.gethostname()
            endpoint: raw | event.  Use 'raw' if field extractions should be skipped.
                see http://docs.splunk.com/Documentation/Splunk/latest/RESTREF/RESTinput#services.2Fcollector.2Fraw

        """
        self.host = host
        self.token = token
        if kwargs is not None:
            self.port = int(kwargs.get('port', 8080))
            self.proto = kwargs.get('proto', 'https')
            self.ssl_verify = False if (kwargs.get('ssl_verify') in ["0", 0, "false", "False", False]) \
                else kwargs.get('cert') or True
            self.source = kwargs.get('source')
            self.index = kwargs.get('index')
            self.sourcetype = kwargs.get('sourcetype')
            self.hostname = kwargs.get('hostname', socket.gethostname())
            self.endpoint = kwargs.get('endpoint', 'event')

        try:
            # Testing connectivity
            s = socket.socket()
            s.settimeout(self.TIMEOUT)
            s.connect((self.host, self.port))

            # Socket accessible.  Establish requests session
            self.r = requests.session()
            self.r.max_redirects = 1
            self.r.verify = self.ssl_verify
            self.r.headers['Authorization'] = "Splunk {}".format(self.token)
            logging.Handler.__init__(self)
        except Exception as err:
            logging.error("Failed to connect to remote Splunk server (%s:%s). Exception: %s"
                          % (self.host, self.port, err))
            raise err
        else:
            self.url = self.URL_PATTERN.format(self.proto, self.host, self.port, self.endpoint)
            s.close()

    def emit(self, record):
        """
        Send log record to Splunk HEC listener
        :param record: string or dictionary. String record is logged as 'message' in Splunk.
        Dictionary is preserved as JSON object.
        :return: None
        """
        data = record.msg

        event = {'host': self.hostname, 'event': data, 'fields': {}}

        # Splunk 7.x does not like empty fields
        if self.source:
            event['source'] = self.source

        if self.sourcetype:
            event['sourcetype'] = self.sourcetype

        if self.index:
            event['index'] = self.index
        # Resort to current time
        else:
            event['time'] = int(time.time())

        # fields
        # This specifies explicit custom fields that are separate from the main "event" data.
        # This method is useful if you don't want to include the custom fields with the event data,
        # but you want to be able to annotate the data with some extra information, such as where it came from.
        # http://dev.splunk.com/view/event-collector/SP-CAAAFB6
        if ('fields' in data.keys() and hasattr(data['fields'], 'items')) or ('time' in data.keys()):
            try:
                for k, v in data['fields'].items():
                    if k in ['host', 'source', 'sourcetype', 'time', 'index']:
                        event[k] = v
                    else:
                        try:
                            if type(v) in [str, list]:
                                event['fields'][k] = v
                            else:
                                # Splunk fails to index event if fields contains values of type other than str or list
                                # i.e HTTP Status: 400, Reason: Bad Request,
                                # Content: {"text":" Error in handling indexed fields", "code":15}
                                event['fields'][k] = str(v)
                        except Exception:
                            pass
            except Exception:
                pass
            else:
                data.pop('fields')

        data = json.dumps(event, sort_keys=True)

        try:
            req = self.r.post(self.url, data=data, timeout=self.TIMEOUT)

            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logging.debug("Failed to emit record to Splunk server (%s:%s).  Exception raised: %s"
                          % (self.host, self.port, err))
            raise err
