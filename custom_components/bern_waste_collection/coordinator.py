from datetime import datetime, timedelta, timezone
import logging

from aiohttp import ClientError

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_UPDATE_INTERVAL, BASE_URL, STREET

_LOGGER = logging.getLogger(__name__)


def parse_pickup_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%d.%m.%Y")


def get_next_pickup(entries):
    """Return next upcoming pickup entry."""
    today = datetime.now().date()

    future_entries = []

    for entry in entries:
        dt = datetime.strptime(entry["date"], "%d.%m.%Y").date()
        if dt >= today:
            future_entries.append((dt, entry))

    if not future_entries:
        return None  # or handle next year if needed

    # Sort by date and return the soonest one
    future_entries.sort(key=lambda x: x[0])
    return future_entries[0][1]


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

                household_entry = get_next_pickup(data["householdWaste"])
                greenwaste_entry = get_next_pickup(data["greenWaste"])
                paper_entry = get_next_pickup(data["paperCollection"])

                return {
                    "household": parse_pickup_date(household_entry["date"]) if household_entry else None,
                    "household_holiday": {
                        "isPublicHoliday": household_entry["isPublicHoliday"],
                        "holidayName": household_entry["holidayName"],
                    } if household_entry else {},

                    "greenwaste": parse_pickup_date(greenwaste_entry["date"]) if greenwaste_entry else None,
                    "greenwaste_holiday": {
                        "isPublicHoliday": greenwaste_entry["isPublicHoliday"],
                        "holidayName": greenwaste_entry["holidayName"],
                    } if greenwaste_entry else {},

                    "paper": parse_pickup_date(paper_entry["date"]) if paper_entry else None,
                    "paper_holiday": {
                        "isPublicHoliday": paper_entry["isPublicHoliday"],
                        "holidayName": paper_entry["holidayName"],
                    } if paper_entry else {},
                }

        except ClientError as err:
            raise UpdateFailed(f"Error fetching data: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")