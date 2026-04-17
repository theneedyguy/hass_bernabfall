from datetime import timedelta, datetime
import logging

from aiohttp import ClientError

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_API_URL, CONF_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class CollectionCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session, config_entry):
        self.api_url = config_entry.data[CONF_API_URL]
        update_interval = config_entry.data[CONF_UPDATE_INTERVAL]

        super().__init__(
            hass,
            _LOGGER,
            name="Bern Waste Managment",
            update_interval=timedelta(seconds=update_interval),
        )
        self.session = session

    async def _async_update_data(self):
        try:
            async with self.session.get(self.api_url) as response:
                data = await response.json()

                household_date = data["householdWaste"][0]["date"]
                greenwaste_date = data["greenWaste"][0]["date"]

                return {
                    "household": household_date,
                    "greenwaste": greenwaste_date
                }

        except ClientError as err:
            raise UpdateFailed(f"Error fetching data: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")