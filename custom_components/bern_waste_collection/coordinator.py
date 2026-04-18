from datetime import datetime, timedelta, timezone
import logging

from aiohttp import ClientError

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_UPDATE_INTERVAL, BASE_URL, STREET

_LOGGER = logging.getLogger(__name__)


def parse_pickup_date(date_str: str) -> datetime:
    """Convert 'DD.MM.' string to next occurrence datetime."""
    today = datetime.now()
    day, month = map(int, date_str.strip(".").split("."))

    # Try this year
    year = today.year
    pickup_date = datetime(year, month, day)

    # If the date has already passed, use next year
    if pickup_date < today:
        pickup_date = datetime(year + 1, month, day)

    # Return as aware datetime in local timezone
    return pickup_date.replace(tzinfo=timezone.utc)


class CollectionCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session, config_entry):
        self.api_url = BASE_URL
        self.street_addr = config_entry.data[STREET]
        update_interval = config_entry.data[CONF_UPDATE_INTERVAL]

        super().__init__(
            hass,
            _LOGGER,
            name="Bern Waste Collection",
            update_interval=timedelta(seconds=update_interval),
        )
        self.session = session

    async def _async_update_data(self):
        try:
            async with self.session.get(self.api_url, params={"address": self.street_addr}) as response:
                data = await response.json()

                household_date_str = data["householdWaste"][0]["date"]
                greenwaste_date_str = data["greenWaste"][0]["date"]

                return {
                    "household": parse_pickup_date(household_date_str),
                    "household_holiday": {
                        "isPublicHoliday": data["householdWaste"][0]["isPublicHoliday"],
                        "holidayName": data["householdWaste"][0]["holidayName"],
                    },
                    "greenwaste": parse_pickup_date(greenwaste_date_str),
                    "greenwaste_holiday": {
                        "isPublicHoliday": data["greenWaste"][0]["isPublicHoliday"],
                        "holidayName": data["greenWaste"][0]["holidayName"],
                    },
                }

        except ClientError as err:
            raise UpdateFailed(f"Error fetching data: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")