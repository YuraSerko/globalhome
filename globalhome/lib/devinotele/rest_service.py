# -*-coding=utf-8-*-
import urllib
import json
import urllib2
import cookielib

class RestApi:
    """ Class for calling REST API methods """

    def __init__(self, login, password, host='https://integrationapi.net/rest'):
        self._login = login
        self._password = password
        self._host = host
        self._get_session_id()

    def _get_session_id(self):
        """ get session identifier
        """
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(self.opener)
        params = urllib.urlencode({'login': self._login, 'password': self._password})
        print "{0}/user/sessionId?{1}".format(self._host, params)
        response = self.opener.open("{0}/user/sessionId?{1}".format(self._host, params))
        data = response.read().decode('utf-8')
        self._session_id = json.loads(data)
        return self._session_id

    def get_balance(self):
        """ get balance
        """
        return self._request("/user/balance?")

    def send_message(self, source_address, destination_address,
                     data, validity=0, send_date_utc=''):
        """ send message
        """
        params = {'sourceAddress': source_address,
                  'destinationAddress': destination_address,
                  'data': data,
                  'validity': validity,
                  'sendDate': send_date_utc}
        return self._request("/sms/send", params, 'post')

    def send_messages_bulk(self, source_address, destination_addresses,
                           data, validity=0, send_date_utc=''):
        """ send messages to many addresses
        """
        params = {'sourceAddress': source_address,
                  'destinationAddresses': destination_addresses,
                  'data': data,
                  'validity': validity,
                  'sendDate': send_date_utc}
        return self._request("/sms/sendbulk", params, 'post')

    def send_message_by_timezone(self, source_address, destination_address,
                                 data, send_date, validity=0):
        """ send message in addressee local time, send_date should be local time
        """
        params = {'sourceAddress': source_address,
                  'destinationAddress': destination_address,
                  'data': data,
                  'validity': validity,
                  'sendDate': send_date}
        return self._request("/sms/sendbytimezone", params, 'post')

    def get_message_state(self, message_id):
        """ getting state for message by its identifier
        """
        params = {'messageId': message_id}
        return self._request("/sms/state?", params)

    def get_statistics(self, start_date, end_date):
        """ getting sent/delivered statistics in datetime range,
        datetimes should be local
        """
        params = {'startDateTime' : start_date,
                  'endDateTime' : end_date}
        return self._request("/sms/statistics?", params)

    def get_incoming_messages(self, start_date_utc, end_date_utc):
        """ getting incoming messages in datetime range,
        datetimes should be UTC
        """
        params = {'minDateUTC' : start_date_utc,
                  'maxDateUTC' : end_date_utc}
        return self._request("/sms/in?", params)

    def _request(self, path, params={}, method='get'):
        params['sessionId'] = self._session_id
        path = self._host + path
        # opener = urllib.request.FancyURLopener({})
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

        try:
            encoded_params = urllib.urlencode(params, True)
            response = self.opener.open(path + encoded_params) if method == 'get' else self.opener.open(path, encoded_params)
        except urllib2.URLError as error:
            if error.code == 401 and error.msg == 'Unauthorized':
                self._get_session_id()
            params['sessionId'] = self._session_id
            encoded_params = urllib.urlencode(params, True)
            response = self.opener.open(path + encoded_params) if method == 'get' else self.opener.open(path, encoded_params)

        data = response.read().decode('utf-8')
        return json.loads(data)

