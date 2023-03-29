"""The HikVision Control integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api_client import ApiClient
from .const import DOMAIN

logger = logging.getLogger(__name__)


PLATFORMS: list[Platform] = [
    Platform.SELECT,
]


class CameraBackend:
    def __init__(self, entry) -> None:
        url = entry.data.get("url")
        username = entry.data.get("username")
        password = entry.data.get("password")

        self.client = ApiClient(url, username, password)
        self.ir_mode = "auto"

    async def update(self):
        self.ir_mode = await self.client.get_ir_mode()

    async def set_ir_mode(self, mode):
        await self.client.set_ir_mode(mode)
        await self.update()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HikVision Control from a config entry."""

    backend = CameraBackend(entry)
    coordinator = DataUpdateCoordinator(
        hass,
        logger,
        name=DOMAIN,
        update_method=backend.update,
        update_interval=timedelta(minutes=1),
    )
    await coordinator.async_request_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "backend": backend,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_update_options(hass, entry: ConfigEntry):
    """Update options."""

    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
