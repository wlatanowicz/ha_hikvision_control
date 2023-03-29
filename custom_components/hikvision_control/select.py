import logging

from homeassistant.components.select import SelectEntity

from .const import DOMAIN

logger = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    backend = hass.data[DOMAIN][entry.entry_id]["backend"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    ir_mode_select = InfraredLightMode(
        entry,
        hass,
        backend,
        coordinator,
    )
    async_add_entities([ir_mode_select], True)
    return True


class InfraredLightMode(SelectEntity):
    def __init__(self, entry, hass, backend, coordinator) -> None:
        super().__init__()
        self.hass = hass
        self.backend = backend
        self.coordinator = coordinator
        self._attr_options = [
            "day",
            "night",
            "auto",
        ]
        self._name = f"{DOMAIN.capitalize()} IR Mode"
        self._unique_id = f"{DOMAIN}__{entry.entry_id}__ir_mode"

    async def async_select_option(self, option: str) -> None:
        await self.backend.set_ir_mode(option)
        await self.coordinator.async_request_refresh()

    @property
    def current_option(self) -> str | None:
        return self.backend.ir_mode

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        """Return a unique id."""
        return self._unique_id
