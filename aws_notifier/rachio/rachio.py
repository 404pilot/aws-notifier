import json
import logging

from requests import Session


class SessionConfig:
    def __init__(
        self,
        read_timeout: int = 60,
        connect_timeout: int = 5,
        accept: str = "application/json",
        content_type: str = "application/json",
        verify: bool = True,
        raise_exception: bool = True,
    ):
        self.read_timeout = read_timeout
        self.connect_timeout = connect_timeout
        self.accept = accept
        self.content_type = content_type
        self.verify = verify
        self.raise_exception = raise_exception


class BaseSession(Session):
    def __init__(self, session_config):
        super().__init__()

        self.session_config = session_config

    def request(self, method, url, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = (
                self.session_config.connect_timeout,
                self.session_config.read_timeout,
            )

        if "verify" not in kwargs:
            kwargs["verify"] = self.session_config.verify

        if "headers" not in kwargs:
            kwargs["headers"] = {}

        headers = kwargs["headers"]

        if "Accept" not in headers:
            headers["Accept"] = self.session_config.accept

        if "Content-Type" not in headers:
            headers["Content-Type"] = self.session_config.content_type

        response = super().request(method, url, **kwargs)

        if 400 <= response.status_code < 600:
            logging.debug(
                "Got api error response, action=%s, api=%s, status=%d, response=%s",
                response.request.method,
                response.url,
                response.status_code,
                response.json(),
            )
        else:
            logging.debug(
                "Got api response ,action=%s, api=%s, status=%d",
                response.request.method,
                response.url,
                response.status_code,
            )

        if self.session_config.raise_exception:
            response.raise_for_status()

        return response

    def prepare_request(self, request):
        p = super().prepare_request(request)

        logging.debug("Calling api... action=%s, api=%s", request.method, request.url)

        return p


class RachioSession(BaseSession):
    def __init__(self, session_config, api_endpoint, api_key):
        super().__init__(session_config)

        self._api_endpoint = api_endpoint
        self._api_key = api_key

    def prepare_request(self, request):
        request.url = f"{self._api_endpoint}/{request.url}"
        p = super().prepare_request(request)

        p.headers["Authorization"] = f"Bearer {self._api_key}"

        return p


class Rachio:
    def __init__(self, api_key):
        self._api_key = api_key
        self._api = "https://api.rach.io/1"
        # internal api usage can be found in rachio web portal
        self._internal_api = "https://cloud-rest.rach.io"

        session_config = SessionConfig()
        self._api_session = RachioSession(session_config=session_config,
                                          api_endpoint=self._api,
                                          api_key=api_key)
        self._internal_api_session = RachioSession(session_config=session_config,
                                                   api_endpoint=self._internal_api,
                                                   api_key=api_key)

    def get_user_id(self):
        with self._api_session as s:
            r = s.get("public/person/info")

            return r.json()["id"]

    def get_device_id(self, user_id):
        with self._api_session as s:
            r = s.get(f"public/person/{user_id}")

            return r.json()["devices"][0]["id"]

    def get_location_id(self, device_id):
        with self._internal_api_session as s:
            r = s.get(f"device/getDevice/{device_id}")

            return r.json()["device"]["locationId"]

    def get_schedules(self, location_id, start_time, end_time):
        # end_time: "2021-08-01T04:59:59.999Z"
        # start_time: "2021-07-01T05:00:00.000Z"
        with self._internal_api_session as s:
            body = {
                "location_id": location_id,
                "start_time": str(start_time.isoformat()),
                "end_time": str(end_time.isoformat()),
            }

            r = s.post("location/getCalendarForTimeRange",
                       data=json.dumps(body))

            return r.json()
