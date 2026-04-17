from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo


from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        CollectionSensor(coordinator, "household", "Household Collection Date", "mdi:trash-can"),
        CollectionSensor(coordinator, "greenwaste", "Greenwaste Collection Date", "mdi:leaf"),
    ])


class CollectionSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, icon):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = key
        self._attr_icon = icon

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            model="Waste Collection API",
            configuration_url="https://api.0x01.host/bernabfall",
            name="Bern Waste Collection",
            manufacturer="Custom",
        )
