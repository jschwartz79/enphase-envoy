import re
import requests
import time
from lxml import etree

SYSTEM_STATS_PAGE = 'home'
PRODUCTION_PAGE = 'production'

class Envoy(object):
    """
    Interface to the Enphase Envoy monitoring device.
    """

    def __init__(self, envoy_ip, cache_timeout=5):
        self._ip = envoy_ip
        self._system_stats = {}
        self._system_production_stats = {}
        self._cache_timeout = cache_timeout
        self._system_stats_last_load = self._system_production_stats_last_load = time.time() - cache_timeout

    def _load_page(self, page):
        url = 'http://{envoy_ip}/{page}'.format(envoy_ip=self._ip, page=page)
        r = requests.get(url)
        if r.status_code != 200:
            print 'Failed to load page: %s' % page
            return None

        return r.text

    def _parse_system_stats(self):
        # Use cached data if the data is less than 'cache_timeout' seconds old.
        if time.time() - self._system_stats_last_load < self._cache_timeout:
            return

        page = self._load_page(SYSTEM_STATS_PAGE)

        # Update last load time for caching
        self._system_stats_last_load = time.time()

        root = etree.HTML(page)

        system_stats = root.xpath(".//td[./h2[contains(text(),'System Statistics')]]")

        # Parse the 'System Statistics' table
        envoy_data = {}
        for k,v in system_stats[0].findall('.//tr'):
            self._system_stats[k.text] = v.text

    def _parse_production_stats(self):
        # Use cached data if the data is less than 'cache_timeout' seconds old.
        if time.time() - self._system_production_stats_last_load < self._cache_timeout:
            return

        page = self._load_page(PRODUCTION_PAGE)

        # Update last load time for caching
        self._system_production_stats_last_load = time.time()

        root = etree.HTML(page)

        system_production = root.xpath(".//table[./tr[./td[contains(text(),'System has been live since')]]]")

        # Parse the 'System Statistics' table
        envoy_data = {}
        for element in system_production[0].findall('.//tr'):
            if len(element.getchildren()) == 1:
                continue
            k, v = element.getchildren()
            self._system_production_stats[k.text] = v.text

    def _format_quantity_unit(self, data):
        m = re.search('([0-9.]+) (\w+)', data)
        return (
            m.group(1),
            m.group(2)
        )

    def current_generation(self):
        """
        Return the current power generation.

        Returns:
            (tuple) Containing: (quantity, unit)
        """
        self._parse_system_stats()
        return self._format_quantity_unit(self._system_stats['Currently generating'])

    def number_of_microinverters(self):
        """
        Return the total number of microinverters.

        Returns:
            (int) Number of microinterters.
        """
        self._parse_system_stats()
        return self._system_stats['Number of Microinverters']

    def number_of_microinverters_online(self):
        """
        Return the number of microinverters currently online.

        Returns:
            (int) Number of microinverters.
        """
        self._parse_system_stats()
        return self._system_stats['Number of Microinverters Online']

    def lifetime_generation(self):
        """
        Return the total power generated over the lifetime of the system.

        Returns:
            (tuple) Containing: (quantity, unit)
        """
        self._parse_system_stats()
        return self._format_quantity_unit(self._system_stats['Lifetime generation'])

    def current_software_version(self):
        """
        Return the current software version of the Envoy monitor.

        Returns:
            (str) software version
        """
        self._parse_system_stats()
        return self._system_stats['Current Software Version']

    def software_build_date(self):
        """
        Return software build date.

        Returns:
            (str) software build date
        """
        self._parse_system_stats()
        return self._system_stats['Software Build Date']

    def last_connection_to_website(self):
        """
        Return the time since last contact with the cloud.

        Returns:
            (tuple) containing: (quantity, unit)
        """
        self._parse_system_stats()
        return self._system_stats['Last connection to website']

    def power_generation_today(self):
        """
        Return the total power generation for today.

        Returns:
            (tuple) containing: (quantity, unit)
        """
        self._parse_production_stats()
        return self._format_quantity_unit(self._system_production_stats['Today'])

    def power_generation_past_week(self):
        """
        Return the total power generation for the past week.

        Returns:
            (tuple) containing: (quantity, unit)
        """
        self._parse_production_stats()
        return self._format_quantity_unit(self._system_production_stats['Past Week'])
