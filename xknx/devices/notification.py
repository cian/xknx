"""Module for managing a notification via KNX."""
from xknx.remote_value import RemoteValueString

from .device import Device


class Notification(Device):
    """Class for managing a notification."""

    def __init__(
        self,
        xknx,
        name,
        group_address=None,
        group_address_state=None,
        device_updated_cb=None,
    ):
        """Initialize notification class."""
        # pylint: disable=too-many-arguments
        super().__init__(xknx, name, device_updated_cb)

        self._message = RemoteValueString(
            xknx,
            group_address=group_address,
            group_address_state=group_address_state,
            device_name=name,
            feature_name="Message",
            after_update_cb=self.after_update,
        )

    def _iter_remote_values(self):
        """Iterate the devices RemoteValue classes."""
        yield self._message

    @classmethod
    def from_config(cls, xknx, name, config):
        """Initialize object from configuration structure."""
        group_address = config.get("group_address")
        group_address_state = config.get("group_address_state")

        return cls(
            xknx,
            name,
            group_address=group_address,
            group_address_state=group_address_state,
        )

    @property
    def message(self):
        """Return the current message."""
        return self._message.value

    async def set(self, message):
        """Set message."""
        cropped_message = message[:14]
        await self._message.set(cropped_message)

    async def process_group_write(self, telegram):
        """Process incoming and outgoing GROUP WRITE telegram."""
        await self._message.process(telegram)

    async def do(self, action):
        """Execute 'do' commands."""
        if action.startswith("message:"):
            await self.set(action[8:])
        else:
            self.xknx.logger.warning(
                "Could not understand action %s for device %s", action, self.get_name()
            )

    def __str__(self):
        """Return object as readable string."""
        return '<Notification name="{}" message="{}" />'.format(
            self.name, self._message.group_addr_str()
        )
