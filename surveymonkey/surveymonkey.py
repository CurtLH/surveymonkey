import logging
from math import ceil
import requests

# set up basic logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Monkey:
    """Base class for interacting with the Survey Monkey API.

    Attributes
    ----------
    base_url : str
        Base URL for the API

    token : str
        API Token from Survey Monkey
    """

    def __init__(self, token):
        """init the Monkey class with required attributes."""
        self.base_url = "https://api.surveymonkey.com/v3"
        self.token = token
        self.session = self._create_session()

    def _create_session(self):
        """initialize an authenticated web session"""
        s = requests.Session()
        s.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        )
        return s

    def get_surveys(self):
        """get all surveys the user currently has access to"""
        r = self.session.get(f"{self.base_url}/surveys")
        if r.status_code == 200:
            return r.json()
        else:
            raise ValueError(f"{r.status_code}")

    def get_survey_details(self, survey_id):
        """get details about about a given survey """
        r = self.session.get(f"{self.base_url}/surveys/{survey_id}/details")
        if r.status_code == 200:
            return r.json()
        else:
            raise ValueError(f"{r.status_code}")

    def _get_survey_response_page(self, survey_id, page_num=1):

        # define the parameters for the request
        params = {
            "page": page_num,
            "per_page": 100,
            "status": "completed",
            "sort_by": "date_modified",
            "sort_order": "desc",
        }

        # submit the request
        r = self.session.get(
            f"{self.base_url}/surveys/{survey_id}/responses/bulk", params=params,
        )

        if r.status_code == 200:
            return r.json()

        else:
            raise ValueError("Request not successful")

    def get_survey_responses(self, survey_id):

        # get the first page of responses
        data = self._get_survey_response_page(survey_id, page_num=1)

        # get the total number of responses
        last_page = ceil(data["total"] / 100)

        # iterate over the pages to get all the responses
        responses = []
        for p in range(1, last_page + 1):
            print(f"Submitting query for page number {p} of {last_page}")
            data = self._get_survey_response_page(survey_id, page_num=p)
            responses.extend(data["data"])

        return responses
