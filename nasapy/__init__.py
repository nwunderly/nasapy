# encoding=utf-8

"""

"""

import datetime
from urllib.parse import urljoin

import requests

from nasapy.api import tle, media_search, media_asset_captions, media_asset_metadata, media_asset_manifest, \
    _check_dates, _donki_request


class Nasa(object):
    r"""
    Class object containing the methods for interacting with NASA API endpoints that require an API key.

    Parameters
    ----------
    key : str, default None
        The generated API key received from the NASA API. Registering for an API key can be done on the `NASA API
        webpage <https://api.nasa.gov/>`_. If :code:`None`, a 'DEMO_KEY' with a much more restricted access limited
        is used.

    Attributes
    ----------
    key : str, None
        The specified key when initializing the class.
    limit_remaining : int
        The number of API calls available.
    mars_weather_limit_remaining : int
        The number of API calls available for the :code:`mars_weather` method.

    Methods
    -------
    picture_of_the_day
        Returns the URL and other information for the NASA Picture of the Day.
    mars_weather
        Returns per-Sol (Martian Days) summary data for each of the last seven available Sols.
    asteroid_feed
        Returns a list of asteroids based on their closest approach date to Earth.
    get_asteroids
        Returns data from the overall asteroid data-set or specific asteroids given an ID.
    coronal_mass_ejection
        Returns data collected on coronal mass ejection events from the Space Weather Database of Notifications,
        Knowledge, Information (DONKI).
    geomagnetic_storm
        Returns data collected on geomagnetic storm events from the Space Weather Database of Notifications, Knowledge,
        Information (DONKI).
    interplantary_shock
        Returns data collected on interplantary shock events from the Space Weather Database of Notifications,
        Knowledge, Information (DONKI).
    solar_flare
        Returns data on solar flare events from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI).
    solar_energetic_particle
        Returns data available from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI) API related to solar energetic particle events.
    magnetopause_crossing
        Returns data available from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI) API related to magnetopause crossing events.
    radiation_belt_enhancement
        Returns data available from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI) API related to radiation belt enhancement events.
    hight_speed_stream
        Returns data available from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI) API related to hight speed stream events.
    wsa_enlil_simulation
        Returns data available from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI) API.
    epic
        The EPIC API provides data on the imagery collected by the DSCOVR's Earth Polychromatic Imaging Camera
        (EPIC).
    earth_imagery
        Retrieves the URL and other information from the Landsat 8 image database for the specified lat/lon location
        and date.
    earth_assets
        Retrieves the datetimes and asset names of available imagery for a specified lat-lon location over a given
        date range. The satellite that takes the images passes over each point approximately once every sixteen days.
    mars_rover
        Retrieves image data collected by the Mars rovers Curiosity, Discovery and Spirit.
    genelab_search
        Retrieves available data from the GeneLab and other bioinformatics databases such as the National Institutes
        of Health (NIH) / National Center for Biotechnology Information (NCBI), Gene Expression Omnibus (GEO), the
        European Bioinformatics Institute's (EBI) Proteomics Identification (PRIDE), and the Argonne National
        Laboratory's (ANL) Metagenomics Rapid Annotations using Subsystems Technology (MG-RAST).
    techport
        Retrieves available NASA project data.

    """
    def __init__(self, key=None):

        self.api_key = key

        self.host = 'https://api.nasa.gov'
        self.limit_remaining = None
        self.mars_weather_limit_remaining = None

    @property
    def api_key(self):
        return self.__api_key

    @property
    def limit_remaining(self):
        return self.__limit_remaining

    @property
    def mars_weather_limit_remaining(self):
        return self.__mars_weather_limit_remaining

    @api_key.setter
    def api_key(self, api_key):
        if api_key is not None:
            self.__api_key = api_key
        else:
            self.__api_key = 'DEMO_KEY'

    @limit_remaining.setter
    def limit_remaining(self, remaining):
        self.__limit_remaining = remaining

    @mars_weather_limit_remaining.setter
    def mars_weather_limit_remaining(self, remaining):
        self.__mars_weather_limit_remaining = remaining

    def picture_of_the_day(self, date=None, hd=False):
        r"""
        Returns the URL and other information for the NASA Picture of the Day.

        Parameters
        ----------
        date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to the  current
            date.
        hd : bool, default False
            If True, returns the associated high-definition image of the Astrononmy Picture of the Day.

        Raises
        ------
        TypeError
            Raised if the parameter :code:`date` is not a string or a datetime object.
        TypeError
            Raised if the parameter :code:`hd` is not boolean.
        HTTPError
            Raised if the returned status code is not 200 (success).

        Returns
        -------
        dict
            Dictionary object of the JSON data returned from the API.

        Examples
        --------
        # Initialize Nasa API Class with a demo key
        >>> n = Nasa()
        # Return today's picture of the day
        >>> n.picture_of_the_day()
        # Return a previous date's picture of the day with the high-definition URL included.
        >>> n.picture_of_the_day('2019-01-01', hd=True)

        """
        if date is not None:
            if not isinstance(date, (str, datetime.datetime)):
                raise TypeError('date parameter must be a string representing a date in YYYY-MM-DD format or a datetime '
                                'object.')

        if not isinstance(hd, bool):
            raise TypeError('hd parameter must be True or False (boolean).')

        if isinstance(date, datetime.datetime):
            date = date.strftime('%Y-%m-%d')

        url = urljoin(self.host + '/planetary/', 'apod')

        r = requests.get(url,
                         params={
                             'api_key': self.api_key,
                             'date': date,
                             'hd': hd
                         })

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason)

        else:
            self.__limit_remaining = r.headers['X-RateLimit-Remaining']
            return r.json()

    def mars_weather(self):
        r"""
        Returns per-Sol (Martian Days) summary data for each of the last seven available Sols.

        Raises
        ------
        HTTPError
            Raised when the returned status code is not 200 (success).

        Returns
        -------
        dict
            Dictionary object repreenting the returned JSON data from the API.

        Examples
        --------
        # Initialize NASA API object with a demo key
        >>> n = NASA()
        # Return the most recent data for the previous seven Sols (Martian Days)
        >>> n.mars_weather()

        Notes
        -----
        Data is provided by NASA's InSight Mars lander and as such data for particular Sols may be recalculated as
        more data is received.

        For more information on the data returned, please see
        `NASA's documentation
        <https://github.com/nasa/api-docs/blob/gh-pages/InSight%20Weather%20API%20Documentation.pdf>`_

        """
        url = self.host + '/insight_weather/'

        r = requests.get(url,
                         params={
                             'api_key': self.__api_key,
                             'ver': 1.0,
                             'feedtype': 'json'
                         })

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason, r.url)

        else:
            self.__mars_weather_limit_remaining = r.headers['X-RateLimit-Remaining']
            return r.json()

    def asteroid_feed(self, start_date, end_date=None):
        r"""
        Returns a list of asteroids based on their closest approach date to Earth.

        Parameters
        ----------
        start_date : str, datetime
            String representing a date in YYYY-MM-DD format or a datetime object.
        end_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to seven days
            after the provided :code:`start_date`.

        Raises
        ------
        TypeError
            Raised if the :code:`start_date` parameter is not a string or a datetime object.
        TypeError
            Raised if the :code:`end_date` parameter is not a string or a datetime object.
        HTTPError
            Raised if the returned status code is not 200 (success).

        Returns
        -------
        dict
            Dictionary representing the returned JSON data from the API.

        Examples
        --------
        # Initialize the NASA API with a demo key.
        >>> n = NASA()
        # Get asteroids approaching Earth at the beginning of 2019.
        >>> n.asteroid_feed(start_date='2019-01-01')

        Notes
        -----
        All the data is from the NASA JPL Asteroid team (http://neo.jpl.nasa.gov/). The API is maintained by the
        `SpaceRocks team <https://github.com/SpaceRocks/>`_

        """
        url = self.host + '/neo/rest/v1/feed'

        start_date, end_date = _check_dates(start_date=start_date, end_date=end_date)

        r = requests.get(url,
                         params={
                             'api_key': self.__api_key,
                             'start_date': start_date,
                             'end_date': end_date
                         })

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason, r.url)

        else:
            self.__limit_remaining = r.headers['X-RateLimit-Remaining']
            return r.json()

    def get_asteroids(self, asteroid_id=None):
        r"""
        Returns data from the overall asteroid data-set or specific asteroids given an ID.

        Parameters
        ----------
        asteroid_id : str, int, default None
            If None, the entire asteroid data set is returned. If an :code:`asteroid_id` is provided, data on that
            specific asteroid is returned.

        Raises
        ------
        HTTPError:
            Raised if the returned status code from the API is not 200 (success).

        Returns
        -------
        dict
            Dictionary object representing the returned JSON data from the NASA API.

        Examples
        --------
        # Initialize NASA API with a demo key.
        >>> n = Nasa()
        # Get entire asteroid data set.
        >>> n.get_asteroids()
        # Get asteroid with ID 3542519
        >>> n.get_asteroids(asteroid_id=3542519)

        Notes
        -----
        All the data is from the NASA JPL Asteroid team (http://neo.jpl.nasa.gov/). The API is maintained by the
        `SpaceRocks team <https://github.com/SpaceRocks/>`_

        """
        url = self.host + '/neo/rest/v1/neo/'

        if asteroid_id is not None:
            url = url + str(asteroid_id)

        else:
            url = url + 'browse/'

        r = requests.get(url,
                         params={
                             'api_key': self.__api_key
                         })

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason, r.url)

        else:
            self.__limit_remaining = r.headers['X-RateLimit-Remaining']
            return r.json()

    def neo_sentry(self, active=True):
        pass

    def coronal_mass_ejection(self, start_date=None, end_date=None,
                              accurate_only=True, speed=0, complete_entry=True, half_angle=0,
                              catalog='ALL', keyword=None):
        r"""
        Returns data collected on coronal mass ejection events from the Space Weather Database of Notifications,
        Knowledge, Information (DONKI).

        Parameters
        ----------
        start_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to 30 days prior
            to the current date in UTC time.
        end_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to the current
            date in UTC time.
        accurate_only : bool, default True
            If True (default), only the most accurate results collected are returned.
        complete_entry : bool, default True
            If True (default), only results with complete data is returned.
        speed : int, default 0
            The lower limit of the speed of the CME event. Default is 0
        half_angle : int, default 0
            The lower limit half angle of the CME event. Default is 0.
        catalog : str, {'ALL', 'SWRC_CATALOG', 'JANG_ET_AL_CATALOG'}
            Specifies which catalog of data to return results. Defaults to 'ALL'.
        keyword : str, default None
            Filter results by a specific keyword.

        Raises
        ------
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        ValueError
            Raised if the :code:`catalog` parameter is not one of {'ALL', 'SWRC_CATALOG', 'JANG_ET_AL_CATALOG'}.
        TypeError
            Raised if parameter :code:`complete_entry` is not boolean (True or False).
        TypeError
            Raised if parameter :code:`accurate_only` is not boolean (True or False).

        Returns
        -------
        list
            List of results representing returned JSON data. If no data is returned, an empty dictionary is returned.

        Examples
        --------
        # Initialize NASA API with a demo key
        >>> n = Nasa()
        # View data from coronal mass ejection events from the last thirty days
        >>> n.coronal_mass_ejection()
        # View all CME events from the beginning of 2019.
        >>> n.coronal_mass_ejection(start_date='2019-01-01', end_date=datetime.datetime.today())

        """
        start_date, end_date = _check_dates(start_date=start_date, end_date=end_date)

        if catalog not in ('ALL', 'SWRC_CATALOG', 'JANG_ET_AL_CATALOG'):
            raise ValueError("catalog parameter must be one of ('ALL', 'SWRC_CATALOG', 'JANG_ET_AL_CATALOG')")

        if not isinstance(complete_entry, bool):
            raise TypeError('complete_entry parameter must be boolean (True or False).')

        if not isinstance(accurate_only, bool):
            raise TypeError('accurate_only parameter must be boolean (True or False).')

        url = self.host + '/DONKI/CMEAnalysis'

        r = requests.get(url,
                         params={
                             'api_key': self.__api_key,
                             'startDate': start_date,
                             'endDate': end_date,
                             'mostAccurateOnly': accurate_only,
                             'completeEntryOnly': complete_entry,
                             'speed': speed,
                             'halfAngle': half_angle,
                             'catalog': catalog,
                             'keyword': keyword
                         })

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason, r.url)

        self.__limit_remaining = r.headers['X-RateLimit-Remaining']

        if r.text == '':
            r = {}
        else:
            r = r.json()

        return r

    def geomagnetic_storm(self, start_date=None, end_date=None):
        r"""
        Returns data collected on geomagnetic storm events from the Space Weather Database of Notifications, Knowledge,
        Information (DONKI).

        Parameters
        ----------
        start_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to 30 days prior
            to the current date in UTC time.
        end_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to the current
            date in UTC time.

        Raises
        ------
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.

        Returns
        -------
        list
            List of results representing returned JSON data. If no data is returned, an empty dictionary is returned.

        Examples
        --------
        # Initialize API connection with a Demo Key
        >>> n = Nasa()
        # Get geomagnetic storm events from the last thirty days.
        >>> n.geomagnetic_storm()
        [{'gstID': '2019-08-31T12:00:00-GST-001',
          'startTime': '2019-08-31T12:00Z',
          'allKpIndex': [{'observedTime': '2019-08-31T15:00Z',
            'kpIndex': 6,
            'source': 'NOAA'},
           {'observedTime': '2019-09-01T15:00Z', 'kpIndex': 6, 'source': 'NOAA'}],
          'linkedEvents': [{'activityID': '2019-08-30T12:17:00-HSS-001'}]}]

        """
        start_date, end_date = _check_dates(start_date=start_date, end_date=end_date)

        url = self.host + '/DONKI/GST'

        r = requests.get(url,
                         params={
                             'api_key': self.__api_key,
                             'startDate': start_date,
                             'endDate': end_date
                         })

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason, r.url)

        self.__limit_remaining = r.headers['X-RateLimit-Remaining']

        if r.text == '':
            r = {}
        else:
            r = r.json()

        return r

    def interplantary_shock(self, start_date=None, end_date=None, location='ALL', catalog='ALL'):
        r"""
        Returns data collected on interplantary shock events from the Space Weather Database of Notifications,
        Knowledge, Information (DONKI).

        Parameters
        ----------
        start_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to 30 days prior
            to the current date in UTC time.
        end_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to the current
            date in UTC time.
        location : str, {'ALL', 'Earth', 'MESSENGER', 'STEREO A', 'STEREO B'}
            Filters returned results to specified location of the interplantary shock event. Defaults to 'ALL'.
        catalog : str, {'ALL', 'SWRC_CATALOG', 'WINSLOW_MESSENGER_ICME_CATALOG'}
            Filters results to a specified catalog of collected data. Defaults to 'ALL'.

        Raises
        ------
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        ValueError
            Raised if :code:`location` parameter is not one of {'ALL', 'Earth', 'MESSENGER', 'STEREO A', 'STEREO B'}
        ValueError
            Raised if :code:`catalog` parameter is not one of {'ALL', 'SWRC_CATALOG', 'WINSLOW_MESSENGER_ICME_CATALOG'}
        TypeError
            Raised if :code:`location` parameter is not a string.
        TypeError
            Raised if :code:`catalog` parameter is not a string.

        Returns
        -------
        list
            List of results representing returned JSON data. If no data is returned, an empty list is returned.

        Examples
        --------

        """
        start_date, end_date = _check_dates(start_date=start_date, end_date=end_date)

        if not isinstance(location, str):
            raise TypeError('location parameter must be a string')

        if not isinstance(catalog, str):
            raise TypeError('catalog parameter must be a string')

        if location not in ('ALL', 'Earth', 'MESSENGER', 'STEREO A', 'STEREO B'):
            raise ValueError(
                "location parameter must be one of {'ALL' (default), 'Earth', 'MESSENGER', 'STEREO A', 'STEREO B'}")

        if catalog not in ('ALL', 'SWRC_CATALOG', 'WINSLOW_MESSENGER_ICME_CATALOG'):
            raise ValueError(
                "catalog parameter must be one of {'ALL' (default) 'SWRC_CATALOG', 'WINSLOW_MESSENGER_ICME_CATALOG'}")

        url = self.host + '/DONKI/IPS'

        r = requests.get(url,
                         params={
                             'api_key': self.__api_key,
                             'startDate': start_date,
                             'endDate': end_date,
                             'location': location,
                             'catalog': catalog
                         })

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason, r.url)

        self.__limit_remaining = r.headers['X-RateLimit-Remaining']

        if r.text == '':
            r = {}
        else:
            r = r.json()

        return r

    def solar_flare(self, start_date=None, end_date=None):
        r"""
        Returns data on solar flare events from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI).

        Parameters
        ----------
        start_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to 30 days prior
            to the current date in UTC time.
        end_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to the current
            date in UTC time.

        Raises
        ------
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.

        Returns
        -------
        list
            If data is available in the specified date range, a list of dictionary objects representing the data from
            the API is returned. If no data is available, an empty dictionary is returned.

        Examples
        --------
        # Initialize API connection with a Demo Key
        >>> n = Nasa()
        # Get solar flare events from May of 2019
        >>> n.solar_flare(start_date='2019-05-01', end_date='2019-05-31')
        [{'flrID': '2019-05-06T05:04:00-FLR-001',
          'instruments': [{'id': 11, 'displayName': 'GOES15: SEM/XRS 1.0-8.0'}],
          'beginTime': '2019-05-06T05:04Z',
          'peakTime': '2019-05-06T05:10Z',
          'endTime': None,
          'classType': 'C9.9',
          'sourceLocation': 'N08E50',
          'activeRegionNum': 12740,
          'linkedEvents': None}]

        """
        self.__limit_remaining, r = _donki_request(url=self.host + '/DONKI/FLR',
                                                   key=self.__api_key,
                                                   start_date=start_date,
                                                   end_date=end_date)

        return r

    def solar_energetic_particle(self, start_date=None, end_date=None):
        r"""
        Returns data available from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI) API related to solar energetic particle events.

        Parameters
        ----------
        start_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to 30 days prior
            to the current date in UTC time.
        end_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to the current
            date in UTC time.

        Raises
        ------
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.

        Returns
        -------
        list
            If data is available in the specified date range, a list of dictionary objects representing the data from
            the API is returned. If no data is available, an empty dictionary is returned.

        Examples
        --------
        # Initialize API connection with a Demo Key
        >>> n = Nasa()
        # Get data from April 2017
        >>> n.solar_energetic_particle(start_date='2017-04-01', end_date='2017-04-30')
        [{'sepID': '2017-04-18T23:39:00-SEP-001',
          'eventTime': '2017-04-18T23:39Z',
          'instruments': [{'id': 6, 'displayName': 'STEREO A: IMPACT 13-100 MeV'}],
          'linkedEvents': [{'activityID': '2017-04-18T19:15:00-FLR-001'},
           {'activityID': '2017-04-18T19:48:00-CME-001'}]}]

        """
        self.__limit_remaining, r = _donki_request(url=self.host + '/DONKI/SEP',
                                                   key=self.__api_key,
                                                   start_date=start_date,
                                                   end_date=end_date)

        return r

    def magnetopause_crossing(self, start_date=None, end_date=None):
        r"""
        Returns data available from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI) API related to magnetopause crossing events.

        Parameters
        ----------
        start_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to 30 days prior
            to the current date in UTC time.
        end_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to the current
            date in UTC time.

        Raises
        ------
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.

        Returns
        -------
        list
            If data is available in the specified date range, a list of dictionary objects representing the data from
            the API is returned. If no data is available, an empty dictionary is returned.

        Examples
        --------
        # Initialize API connection with a Demo Key
        >>> n = Nasa()
        # Get data on magnetopause crossing events from 2018 to the current date.
        >>> n.magnetopause_crossing(start_date='2018-01-01')
        [{'mpcID': '2018-05-05T14:33:00-MPC-001',
          'eventTime': '2018-05-05T14:33Z',
          'instruments': [{'id': 15, 'displayName': 'MODEL: SWMF'}],
          'linkedEvents': [{'activityID': '2018-05-05T09:27:00-HSS-001'}]}]

        """
        self.__limit_remaining, r = _donki_request(url=self.host + '/DONKI/MPC',
                                                   key=self.__api_key,
                                                   start_date=start_date,
                                                   end_date=end_date)

        return r

    def radiation_belt_enhancement(self, start_date=None, end_date=None):
        r"""
        Returns data available from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI) API related to radiation belt enhancement events.

        Parameters
        ----------
        start_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to 30 days prior
            to the current date in UTC time.
        end_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to the current
            date in UTC time.

        Raises
        ------
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.

        Returns
        -------
        list
            If data is available in the specified date range, a list of dictionary objects representing the data from
            the API is returned. If no data is available, an empty dictionary is returned.

        Examples
        --------
        # Initialize API connection with a Demo Key
        >>> n = Nasa()
        # Get data on radiation belt enhancement events from the last 30 days.
        >>> n.radiation_belt_enhancement()
        [{'rbeID': '2019-08-31T18:50:00-RBE-001',
          'eventTime': '2019-08-31T18:50Z',
          'instruments': [{'id': 14, 'displayName': 'GOES13: SEM/EPS >0.8 MeV'}],
          'linkedEvents': [{'activityID': '2019-08-30T12:17:00-HSS-001'}]}]

        """
        self.__limit_remaining, r = _donki_request(url=self.host + '/DONKI/RBE',
                                                   key=self.__api_key,
                                                   start_date=start_date,
                                                   end_date=end_date)

        return r

    def hight_speed_stream(self, start_date=None, end_date=None):
        r"""
        Returns data available from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI) API related to hight speed stream events.

        Parameters
        ----------
        start_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to 30 days prior
            to the current date in UTC time.
        end_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to the current
            date in UTC time.

        Raises
        ------
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.

        Returns
        -------
        list
            If data is available in the specified date range, a list of dictionary objects representing the data from
            the API is returned. If no data is available, an empty dictionary is returned.

        Examples
        --------
        # Initialize API connection with a Demo Key
        >>> n = Nasa()
        # Get data on hight speed stream events from the beginning of September 2019.
        >>> n.hight_speed_stream()
        [{'hssID': '2019-09-09T01:22:00-HSS-001',
          'eventTime': '2019-09-09T01:22Z',
          'instruments': [{'id': 9, 'displayName': 'ACE: SWEPAM'}],
          'linkedEvents': None},
         {'hssID': '2019-09-12T20:21:00-HSS-001',
          'eventTime': '2019-09-12T20:21Z',
          'instruments': [{'id': 9, 'displayName': 'ACE: SWEPAM'},
           {'id': 10, 'displayName': 'ACE: MAG'}],
          'linkedEvents': None},
         {'hssID': '2019-09-17T03:00:00-HSS-001',
          'eventTime': '2019-09-17T03:00Z',
          'instruments': [{'id': 20, 'displayName': 'STEREO A: IMPACT'},
           {'id': 21, 'displayName': 'STEREO A: PLASTIC'}],
          'linkedEvents': None}]

        """
        self.__limit_remaining, r = _donki_request(url=self.host + '/DONKI/HSS',
                                                   key=self.__api_key,
                                                   start_date=start_date,
                                                   end_date=end_date)

        return r

    def wsa_enlil_simulation(self, start_date=None, end_date=None):
        r"""
        Returns data available from the Space Weather Database of Notifications, Knowledge, Information
        (DONKI) API.

        Parameters
        ----------
        start_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to 30 days prior
            to the current date in UTC time.
        end_date : str, datetime, default None
            String representing a date in YYYY-MM-DD format or a datetime object. If None, defaults to the current
            date in UTC time.

        Raises
        ------
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.
        TypeError
            Raised if parameter :code:`start_date` is not a string representing a date in YYYY-MM-DD format or
            a datetime object.

        Returns
        -------
        list
            If data is available in the specified date range, a list of dictionary objects representing the data from
            the API is returned. If no data is available, an empty dictionary is returned.

        Examples
        --------
        # Initialize API connection with a Demo Key
        >>> n = Nasa()
        # Get data from the first simulation performed in 2019.
        >>> wsa = n.wsa_enlil_simulation(start_date='2019-01-01')
        >>> wsa[0]
        {'simulationID': 'WSA-ENLIL/14394/1',
         'modelCompletionTime': '2019-01-03T18:26Z',
         'au': 2.0,
         'cmeInputs': [{'cmeStartTime': '2019-01-02T23:12Z',
           'latitude': -27.0,
           'longitude': 45.0,
           'speed': 430.0,
           'halfAngle': 18.0,
           'time21_5': '2019-01-03T07:15Z',
           'isMostAccurate': True,
           'levelOfData': 1,
           'ipsList': [],
           'cmeid': '2019-01-02T23:12:00-CME-001'}],
         'estimatedShockArrivalTime': None,
         'estimatedDuration': None,
         'rmin_re': None,
         'kp_18': None,
         'kp_90': None,
         'kp_135': None,
         'kp_180': None,
         'isEarthGB': False,
         'impactList': None}

        """
        self.__limit_remaining, r = _donki_request(url=self.host + '/DONKI/WSAEnlilSimulations',
                                                   key=self.__api_key,
                                                   start_date=start_date,
                                                   end_date=end_date)

        return r

    def epic(self, color='natural', date=None, available=False):
        r"""
        The EPIC API provides data on the imagery collected by the DSCOVR's Earth Polychromatic Imaging Camera
        (EPIC).

        Parameters
        ----------
        color : str, {'natural', 'enhanced'}
            Specifies the type of imagery to return. Must be one of 'natural' (default) or 'enhanced'
        date : str, datetime, default None
            String representing a date in 'YYYY-MM-DD' format or a datetime object.
        available : bool, default False
            Alternative listing of all dates with specified color imagery.

        Raises
        ------
        TypeError
            Raised if parameter :code:`available` is not boolean (True or False).
        TypeError
            Raised if parameter :code:`date` is not a string or a datetime object.
        ValueError
            Raised if parameter :code:`color` is not one of 'natural' or 'enhanced'

        Returns
        -------
        list
            List of dictionaries representing the returned JSON data from the EPIC API.

        Examples
        --------
        # Initialize API connection with a Demo Key
        >>> n = Nasa()
        # Get EPIC data from the beginning of 2019.
        >>> e = n.epic(date='2019-01-01')
        # Print the first result
        >>> e[0]
        {'identifier': '20190101015633',
         'caption': "This image was taken by NASA's EPIC camera onboard the NOAA DSCOVR spacecraft",
         'image': 'epic_RGB_20190101015633',
         'version': '02',
         'centroid_coordinates': {'lat': -27.281877, 'lon': 155.325443},
         'dscovr_j2000_position': {'x': 350941.733992,
          'y': -1329357.949188,
          'z': -711000.841667},
         'lunar_j2000_position': {'x': -281552.637877,
          'y': -263898.385852,
          'z': 34132.662255},
         'sun_j2000_position': {'x': 25746688.614416,
          'y': -132882102.563308,
          'z': -57603901.841971},
         'attitude_quaternions': {'q0': 0.621256,
          'q1': 0.675002,
          'q2': 0.397198,
          'q3': 0.025296},
         'date': '2019-01-01 01:51:44',
         'coords': {'centroid_coordinates': {'lat': -27.281877, 'lon': 155.325443},
          'dscovr_j2000_position': {'x': 350941.733992,
           'y': -1329357.949188,
           'z': -711000.841667},
          'lunar_j2000_position': {'x': -281552.637877,
           'y': -263898.385852,
           'z': 34132.662255},
          'sun_j2000_position': {'x': 25746688.614416,
           'y': -132882102.563308,
           'z': -57603901.841971},
          'attitude_quaternions': {'q0': 0.621256,
           'q1': 0.675002,
           'q2': 0.397198,
           'q3': 0.025296}}}

        Notes
        -----
        If a :code:`date` is not given and :code:`available` is :code:`False`, a listing of all dates with the
        specified color imagery is returned using the :code:`all` endpoint of the EPIC API.

        The EPIC API provides information on the daily imagery collected by DSCOVR's Earth Polychromatic Imaging
        Camera (EPIC) instrument. Uniquely positioned at the Earth-Sun Lagrange point, EPIC provides full disc
        imagery of the Earth and captures unique perspectives of certain astronomical events such as lunar transits
        using a 2048x2048 pixel CCD (Charge Coupled Device) detector coupled to a 30-cm aperture Cassegrain telescope.

        """
        url = self.host + '/EPIC/api/'

        if color not in ('natural', 'enhanced'):
            raise ValueError("color parameter must be 'natural' (default), or 'enhanced'.")

        if not isinstance(available, bool):
            raise TypeError('available parameter must be boolean (True or False).')

        if date is not None:
            if not isinstance(date, (str, datetime.datetime)):
                raise TypeError("date parameter must be a string representing a date in YYYY-MM-DD format or a "
                                "datetime object.")

            if isinstance(date, datetime.datetime):
                date = date.strftime('%Y-%m-%d')

            url = url + '{color}/date/{date}'.format(date=date, color=color)

        elif available:
            url = url + '{color}/available'.format(color=color)

        else:
            url = url + '{color}/all'.format(color=color)

        r = requests.get(url,
                         params={'api_key': self.__api_key})

        if r.status_code != 200 or r.text == '':
            r = {}
        else:
            self.__limit_remaining = r.headers['X-RateLimit-Remaining']
            r = r.json()

        return r

    def earth_imagery(self, lat, lon, dim=0.025, date=None, cloud_score=False):
        r"""
        Retrieves the URL and other information from the Landsat 8 image database for the specified lat/lon location
        and date.

        Parameters
        ----------
        lat : int, float
            Latitude
        lon : int, float
            Longitude
        dim : float, default 0.025
            Width and height of the image in degrees.
        date : str, datetime, default None
            Date the image was taken. If specified, must be a string representing a date in 'YYYY-MM-DD' format or a
            datetime object. If None, the most recent image available from the current date is returned.
        cloud_score : bool, default False
            Calculate the percentage of the image covered by clouds.

        Raises
        ------
        TypeError
            Raised if :code:`cloud_score` parameter is not boolean (True or False)
        TypeError
            Raised if :code:`lat` parameter is not an int or float
        TypeError
            Raised if :code:`lon` parameter is not an int or float
        TypeError
            Raised if :code:`dim` parameter is not a float
        TypeError
            Raised if :code:`date` parameter is not a string or a datetime object.
        ValueError
            Raised if :code:`lat` parameter is not between :math:`[-90, 90]`
        ValueError
            Raised if :code:`lon` parameter is not between :math:`[-180, 180]`

        Returns
        -------
        dict
            Dictionary object representing the returned JSON data from the API.

        Examples
        --------
        # Initialize API connection with a Demo Key
        >>> n = Nasa()
        # Get imagery at latitude 1.5, longitude 100.75 and include the computed cloud score calculation.
        >>> n.earth_imagery(lon=100.75, lat=1.5, cloud_score=True)
        {'cloud_score': 0.9947187123297982,
         'date': '2014-01-03T03:30:22',
         'id': 'LC8_L1T_TOA/LC81270592014003LGN00',
         'resource': {'dataset': 'LC8_L1T_TOA', 'planet': 'earth'},
         'service_version': 'v1',
         'url': 'https://earthengine.googleapis.com/api/thumb?thumbid=9081d44f6984d0e4791922804beb54a4&token=e5c9e249894564f93533f02dbd87a1a3'}

        """
        url = self.host + '/planetary/earth/imagery/'

        if not isinstance(cloud_score, bool):
            raise TypeError('cloud score parameter must be boolean (True or False).')
        if not isinstance(lat, (int, float)):
            raise TypeError('lat parameter must be an int or float')
        if not isinstance(lon, (int, float)):
            raise TypeError('lon parameter must be an int or float')
        if not isinstance(dim, float):
            raise TypeError('dim parameter must be a float')

        if not -90 <= lat <= 90:
            raise ValueError('latitudes values range from -90 to 90')
        if not -180 <= lon <= 180:
            raise ValueError('longitude values range from -180 to 180')

        if date is not None:
            if not isinstance(date, (str, datetime.datetime)):
                raise TypeError('date parameter must be a string representing a date in YYYY-MM-DD format or a '
                                'datetime object.')

            if isinstance(date, datetime.datetime):
                date = date.strftime('%Y-%m-%d')

        r = requests.get(url,
                         params={
                             'lon': lon,
                             'lat': lat,
                             'dim': dim,
                             'date': date,
                             'cloud_score': cloud_score,
                             'api_key': self.__api_key
                         })

        if r.status_code != 200 or r.text == '':
            r = {}
        else:
            self.__limit_remaining = r.headers['X-RateLimit-Remaining']
            r = r.json()

        return r

    def earth_assets(self, lat, lon, begin_date, end_date=None):
        r"""
        Retrieves the datetimes and asset names of available imagery for a specified lat-lon location over a given
        date range. The satellite that takes the images passes over each point approximately once every sixteen days.

        Parameters
        ----------
        lat : int, float
            Latitude
        lon : int, float
            Longitude
        begin_date : str, datetime
            Beginning of date range in which to search for available assets.
        end_date : str, datetime, default None
            End of date range in which to search for available assets. If not specified, defaults to the current date.

        Raises
        ------
        ValueError
            Raised if :code:`lat` parameter is not between :math:`[-90, 90]`
        ValueError
            Raised if :code:`lon` parameter is not between :math:`[-180, 180]`
        TypeError
            Raised if :code:`begin_date` parameter is not a string representative of a datetime or a datetime object.
        TypeError
            Raised if :code:`end_date` parameter is not a string representative of a datetime or a datetime object.

        Returns
        -------
        dict
            Dictionary object representing the returned JSON data from the API.

        Notes
        -----
        The assets endpoint is meant to support the imagery endpoint by making it easier for users to find available
        imagery for a given location.

        """
        url = self.host + '/planetary/earth/assets'

        if not isinstance(begin_date, (str, datetime.datetime)):
            raise TypeError('begin date parameter must be a string representing a date in YYYY-MM-DD format or a '
                            'datetime object.')

        if isinstance(begin_date, datetime.datetime):
            begin_date = begin_date.strftime('%Y-%m-%d')

        if end_date is not None:
            if not isinstance(end_date, (str, datetime.datetime)):
                raise TypeError('end date parameter must be a string representing a date in YYYY-MM-DD format or a '
                                'datetime object.')

            if isinstance(end_date, datetime.datetime):
                end_date = end_date.strftime('%Y-%m-%d')

        if not -90 <= lat <= 90:
            raise ValueError('latitudes values range from -90 to 90')
        if not -180 <= lon <= 180:
            raise ValueError('longitude values range from -180 to 180')

        r = requests.get(url,
                         params={
                             'api_key': self.__api_key,
                             'lat': lat,
                             'lon': lon,
                             'begin_date': begin_date,
                             'end_date': end_date
                         })

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason, r.url)

        else:
            self.__limit_remaining = r.headers['X-RateLimit-Remaining']

        return r.json()

    def mars_rover(self, sol=None, earth_date=None, camera='all', rover='curiosity', page=1):
        r"""
        Retrieves image data collected by the Mars rovers Curiosity, Discovery and Spirit.

        Parameters
        ----------
        sol : int, None (default)
            The sol (Martian rotation or day) on which the images were collected. Either this parameter or
            :code:`earth_date` must be provided. The parameter :code:`earth_date` is an alternative parameter for
            searching for a specific date. The sol values count up from the rover's landing date, for example, the
            Curiosity's 100th sol would be the 100th Martian rotation since the rover landed.
        earth_date : str, datetime, None (default)
            Alternative search parameter for finding data on a specific date. Must be a string representing a date
            in 'YYYY-MM-DD' format or a datetime object. Either :code:`earth_date` or :code:`sol` must be specified.
        camera : str, {'all', FHAZ', 'RHAZ', 'MAST', 'CHEMCAM', 'MAHLI', 'MARDI', 'NAVCAM', 'PANCAM', 'MINITES'}
            Filter results to a specific camera on the Mars Curiosity, Opportunity or Spirit rovers. Defaults to 'all',
            which includes all cameras.
        page : int, default 1
            25 results per page are returned.
        rover : str, {'curiosity', 'opportunity', 'spirit'}
            Specifies the Mars rover to return data. Defaults to the Curiosity rover which has more available cameras.

        Raises
        ------
        ValueError
            Raised if both :code:`sol` and :code:`earth_date` parameters are not specified.
        ValueError
            Raised if the :code:`camera` parameter is not one of 'all' (default), 'FHAZ', 'RHAZ', 'MAST', 'CHEMCAM', "
            "'MAHLI', 'MARDI', 'NAVCAM', 'PANCAM', or 'MINITES'
        ValueError
            Raised if :code:`rover` parameter is not one of 'curiosity' (default), 'opportunity', 'spirit'
        TypeError
            Raised if :code:`earth_date` (if provided) is not a string or a datetime object.

        Returns
        -------
        list
            List of dictionaries representing the returned JSON data from the Mars Rover API.

        Examples
        --------
        # Initialize API connection with a Demo Key
        >>> n = Nasa()
        # Return image data collected on Curiosity's 1000th sol.
        >>> r = n.mars_rover(sol=1000)
        # Print the first result in the list collection.
        {'id': 102693,
         'sol': 1000,
         'camera': {'id': 20,
          'name': 'FHAZ',
          'rover_id': 5,
          'full_name': 'Front Hazard Avoidance Camera'},
         'img_src': 'http://mars.jpl.nasa.gov/msl-raw-images/proj/msl/redops/ods/surface/sol/01000/opgs/edr/fcam/FLB_486265257EDR_F0481570FHAZ00323M_.JPG',
         'earth_date': '2015-05-30',
         'rover': {'id': 5,
          'name': 'Curiosity',
          'landing_date': '2012-08-06',
          'launch_date': '2011-11-26',
          'status': 'active',
          'max_sol': 2540,
          'max_date': '2019-09-28',
          'total_photos': 366206,
          'cameras': [{'name': 'FHAZ', 'full_name': 'Front Hazard Avoidance Camera'},
           {'name': 'NAVCAM', 'full_name': 'Navigation Camera'},
           {'name': 'MAST', 'full_name': 'Mast Camera'},
           {'name': 'CHEMCAM', 'full_name': 'Chemistry and Camera Complex'},
           {'name': 'MAHLI', 'full_name': 'Mars Hand Lens Imager'},
           {'name': 'MARDI', 'full_name': 'Mars Descent Imager'},
           {'name': 'RHAZ', 'full_name': 'Rear Hazard Avoidance Camera'}]}}

        """
        if sol is not None and earth_date is not None:
            raise ValueError('either the sol or earth_date parameter should be specified, not both.')

        cameras = ['FHAZ', 'RHAZ', 'MAST', 'CHEMCAM', 'MAHLI', 'MARDI', 'NAVCAM', 'PANCAM', 'MINITES', 'all']

        if camera not in cameras:
            raise ValueError("camera parameter must be one of 'all' (default), 'FHAZ', 'RHAZ', 'MAST', 'CHEMCAM', "
                             "'MAHLI', 'MARDI', 'NAVCAM', 'PANCAM', or 'MINITES'")

        if earth_date is not None:
            if not isinstance(earth_date, (str, datetime.datetime)):
                raise TypeError('end date parameter must be a string representing a date in YYYY-MM-DD format or a '
                                'datetime object.')

            if isinstance(earth_date, datetime.datetime):
                earth_date = earth_date.strftime('%Y-%m-%d')

        if str.lower(rover) not in ('curiosity', 'opportunity', 'spirit'):
            raise ValueError("rover parameter must be one of 'curiosity' (default), 'opportunity', or 'spirit'.")

        url = self.host + '/mars-photos/api/v1/rovers/{rover}/photos'.format(rover=str.lower(rover))

        params = {
            'page': page,
            'api_key': self.__api_key
        }

        if sol is not None:
            params['sol'] = sol
        else:
            params['earth_date'] = earth_date

        if camera != 'all':
            params['camera'] = camera

        r = requests.get(url,
                         params=params)

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason, r.url)

        else:
            self.__limit_remaining = r.headers['X-RateLimit-Remaining']

        return r.json()['photos']

    def exoplanets(self, table, select, count, colset, where, order, ra, dec):
        host = 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?'

        r = requests.get(host,
                         params={
                             'api_key': self.__api_key,
                             'table': table,
                             'select': select,
                             'count': count,
                             'colset': colset,
                             'where': where,
                             'order': order,
                             'ra': ra,
                             'dec': dec,
                             'format': 'json'
                         })

        return r

    def genelab_search(self, term=None, database='cgene', page=0, size=25, sort=None, order='desc',
                       ffield=None, fvalue=None):
        r"""
        Retrieves available data from the GeneLab and other bioinformatics databases such as the National Institutes
        of Health (NIH) / National Center for Biotechnology Information (NCBI), Gene Expression Omnibus (GEO), the
        European Bioinformatics Institute's (EBI) Proteomics Identification (PRIDE), and the Argonne National
        Laboratory's (ANL) Metagenomics Rapid Annotations using Subsystems Technology (MG-RAST).

        Parameters
        ----------
        term : str, default None
            Search by specific keyword(s). Case-insensitive boolean operators (AND, OR, NOT) can be used as well
            to include and filter specific keywords.
        database : str, {'cgene', 'nih_geo_gse', 'ebi_pride', 'mg_rast'}
            Determines the database(s) to query. Defaults to the 'cgene' (GeneLab) database, but other available
            databases include 'nih_geo_gse' (NIH GEO), 'ebi_pride' (EBI PRIDE), or 'mg_rast' (MG-RAST). Multiple
            databases can be queried by separating values with commas. For example,
            'cgene,nih_geo_gse,ebi_pride,mg_rast' will query all available databases.
        page : int, default 0
            Specifies the page of results to return. Defaults to the first page (0).
        size : int, default 25
            Specifies the number of results to return per page. Default is 25 results per page.
        sort : str, default None
            Sorts by a specific field name in the returned JSON data.
        order : str, {'desc', 'asc'}
            Determines the sorting order. Must be one of 'desc' (descending) or 'asc' (ascending).
        ffield : str, default None
            Filters the returned data based on the defined field. Should be paired with the :code:`fvalue` parameter.
            Only the 'cgene' (GeneLab) database can be filtered.
        fvalue : str, default None
            Filters the returned data based on value or values in the specified :code:`ffield` parameter field. Only
            the 'cgene' (GeneLab) database can be filtered.

        Raises
        ------
        ValueError
            Raised if :code:`order` parameter is not one of 'desc' (default), or 'asc'.
        ValueError
            Raised if :code:`page` parameter is less than 0.
        ValueError
            Raised if :code:`size` parameter is 0 or less.
        HTTPError
            Raised if result does not have a 200 status code.

        Returns
        -------
        dict
            Dictionary object representing the returned JSON data.

        Notes
        -----
        The `GeneLab public data repository <https://genelab-data.ndc.nasa.gov/genelab/projects>`_ provides the same
        functionality as the API in a searchable HTML interface. For more information on the available bioinformatics
        databases, please see the following links:
        `Gene Expression Omnibus (GEO) <https://www.ncbi.nlm.nih.gov/geo/>`_
        `European Bioinformatics Institute (EBI) <https://www.ebi.ac.uk/pride/archive/>`_
        `Argonne National Laboratorys (ANL) <http://www.mg-rast.org>`_

        """
        url = 'https://genelab-data.ndc.nasa.gov/genelab/data/search'

        if order not in ('desc', 'asc'):
            raise ValueError('order parameter must be "desc" (descending, default), or "asc" (ascending)')

        if page < 0:
            raise ValueError('page parameter must be at least 0 (start)')

        if size <= 0:
            raise ValueError('size of results to return cannot be 0 or less.')

        r = requests.get(url,
                         params={
                             'term': term,
                             'sort': sort,
                             'type': database,
                             'from': page,
                             'size': size,
                             'order': str.upper(order),
                             'ffield': ffield,
                             'fvalue': fvalue,
                             'api_key': self.__api_key
                         })

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason, r.url)

        return r.json()

    def techport(self, project_id=None, last_updated=None, return_format='json'):
        r"""
        Retrieves available NASA project data.

        Parameters
        ----------
        project_id : str, int, default None
            The ID of the project record. If not specified, all available projects will be returned.
        last_updated : str, datetime
            Returns projects only updated after the specified date. Must be a string representing a date in
            'YYYY-MM-DD' format or a datetime object.
        return_format : str, {'json', 'xml'}
            Specifies the return format of the data. Defaults to 'json', but 'xml' formatted data is also available.

        Raises
        ------
        ValueError
            Raised if :code:`return_foramt` is not one of 'json' (default) or 'xml'.
        TypeError
            Raised if :code:`last_updated` is not a string or a datetime object.

        Returns
        -------
        dict or str
            If :code:`return_format` is 'json', a dictionary representing the JSON formatted data is returned.
            Otherwise, a string formatted for XML is returned.

        """
        url = self.host + '/techport/api/projects/'

        if return_format not in ('json', 'xml'):
            raise ValueError("type parameter must be one of 'json' (default), or 'xml'.")

        if last_updated is not None:
            if not isinstance(last_updated, (str, datetime.datetime)):
                raise TypeError('end date parameter must be a string representing a date in YYYY-MM-DD format or a '
                                'datetime object.')

            if isinstance(last_updated, datetime.datetime):
                last_updated = last_updated.strftime('%Y-%m-%d')

        if project_id is None:
            r = requests.get(url,
                             params={'updatedSince': last_updated,
                                     'api_key': self.__api_key})
        else:
            url = url + '{project_id}'.format(project_id=project_id)

            if return_format == 'xml':
                url = url + '.xml'

            r = requests.get(url,
                             params={'api_key': self.__api_key})

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason, r.url)

        self.__limit_remaining = r.headers['X-RateLimit-Remaining']

        if return_format == 'xml':
            r = r.text
        else:
            r = r.json()

        return r

    # def mars_mission_manifest(self, rover):
    #     url = self.host + '/mars-photos/api/manifests/{rover}'.format(rover=rover)
    #
    #     r = requests.get(url)
    #
    #     return r

    # def patents(self, query, concept_tags=False, limit=None):
    #     url = self.host + '/patents/content'
    #
    #     if limit is not None:
    #         if not isinstance(limit, int):
    #             raise TypeError('limit parameter must None (return all results) or an int.')
    #
    #     if not isinstance(concept_tags, bool):
    #         raise TypeError('concept_tags parameter must be boolean (True or False).')
    #
    #     r = requests.get(url,
    #                      params={
    #                          'query': query,
    #                          'limit': limit,
    #                          'api_key': self.__api_key
    #                      })
    #
    #     if r.status_code != 200 or r.text == '':
    #         r = {}
    #     else:
    #         self.__limit_remaining = r.headers['X-RateLimit-Remaining']
    #         r = r.json()
    #
    #     return r
