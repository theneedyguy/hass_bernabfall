from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo


from .const import DOMAIN, STREET, BASE_URL


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        CollectionSensor(coordinator, "household", "Household Collection Date", "mdi:trash-can"),
        CollectionSensor(coordinator, "greenwaste", "Greenwaste Collection Date", "mdi:leaf"),
        CollectionSensor(coordinator, "paper", "Paper Collection Date", "mdi:newspaper"),
    ])


class CollectionSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, icon):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self._key}_{self.coordinator.config_entry.entry_id}"
        self._attr_icon = icon

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            model="Waste Collection API",
            configuration_url=BASE_URL,
            name=f"Bern Waste Collection ({self.coordinator.config_entry.data.get(STREET)})",
            manufacturer="Custom",
        )

    @property
    def extra_state_attributes(self):
        """Return additional attributes for the sensor."""
        data = self.coordinator.data
        # Look for a corresponding holiday flag/name
        if self._key in data:
            holiday_info = data.get(f"{self._key}_holiday", {})
            # holiday_info could be like: {"isPublicHoliday": True, "holidayName": "Easter"}
            return holiday_info or {}
        return {}
