"""CAN FD Virtual Bus with two-phase settle/sample arbitration.

Phase 1 (write):  every driver writes its intended bit.
Phase 2 (settle): asyncio.sleep(0) yields so ALL writers complete.
Phase 3 (sample): every driver reads the resolved bus and checks for loss.

This eliminates the race where a driver resolves before another has written.
"""

import asyncio


class CANFDBus:
    """Logical CAN bus with wired-AND contention resolution."""

    def __init__(self):
        self.drivers = {}

    def register(self, node_id: int):
        self.drivers[node_id] = 1  # recessive by default

    def _resolve(self) -> int:
        """Wired-AND: dominant (0) overrides recessive (1)."""
        return 0 if 0 in self.drivers.values() else 1

    async def drive_bit(self, node_id: int, bit: int, bit_time_ns: float = 1.0) -> bool:
        """
        Drive one bit through the three-phase protocol.

        Returns True if the bit was driven successfully (no arbitration loss).
        Returns False if arbitration was lost (wanted 1, bus resolved to 0).
        """
        # Phase 1: Write
        self.drivers[node_id] = bit

        # Phase 2: Settle — yield so all drivers finish writing
        await asyncio.sleep(0)

        # Phase 3: Sample
        bus_level = self._resolve()
        if bit == 1 and bus_level == 0:
            # Arbitration lost: stop driving, go recessive
            self.drivers[node_id] = 1
            return False

        # Phase 4: Hold for bit time
        if bit_time_ns > 0:
            await asyncio.sleep(bit_time_ns / 1e9)

        # Phase 5: Release
        self.drivers[node_id] = 1
        return True


class CANFDBusDriver:
    """High-level driver that sends frames over the virtual bus."""

    def __init__(self, bus: CANFDBus, node_id: int):
        self.bus = bus
        self.node_id = node_id
        self.bus.register(node_id)
        self.arbitration_lost = False
        self.lost_at_bit_index = -1

    async def send_frame(self, bitstream: list[int], bit_time_ns: float = 1.0) -> bool:
        """
        Send a pre-stuffed bitstream. Handles arbitration loss gracefully.

        Returns True if the entire frame was transmitted successfully.
        Returns False if arbitration was lost mid-frame.
        """
        self.arbitration_lost = False
        self.lost_at_bit_index = -1

        for i, bit in enumerate(bitstream):
            success = await self.bus.drive_bit(self.node_id, bit, bit_time_ns)
            if not success:
                self.arbitration_lost = True
                self.lost_at_bit_index = i
                return False

        return True
