"""CAN FD Virtual Bus Model with wired-AND resolution and arbitration.

This module provides a logical bus where dominant (0) overrides recessive (1).
Drivers register with the bus and check for arbitration loss bit-by-bit.
"""
import asyncio


class CANFDBus:
    """Logical CAN bus resolving wired-AND contention."""
    
    def __init__(self):
        # Maps node_id -> intended_bit (default 1 = recessive)
        self.drivers = {}

    def register(self, node_id: int):
        """Register a new driver on the bus."""
        self.drivers[node_id] = 1

    def _resolve(self) -> int:
        """Resolve the bus level: 0 dominates 1."""
        return 0 if 0 in self.drivers.values() else 1

    async def drive_bit(self, node_id: int, bit: int, bit_time_ns: float = 0.0) -> bool:
        """
        Attempt to drive a bit onto the bus.
        
        Returns:
            True if the bit was successfully driven (or matched the bus).
            False if arbitration was lost (driver wanted 1, but bus resolved to 0).
        """
        self.drivers[node_id] = bit
        bus_level = self._resolve()
        
        # Arbitration loss: we tried to send recessive (1), but someone sent dominant (0)
        if bit == 1 and bus_level == 0:
            # Node loses arbitration: immediately stop driving (go recessive)
            self.drivers[node_id] = 1
            return False
        
        # Wait for the bit time to elapse (simulated time for unit tests)
        if bit_time_ns > 0:
            await asyncio.sleep(bit_time_ns / 1e9)
        
        # Return to recessive state after the bit is sent (simplified for bit-level model)
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

    async def send_frame(self, bitstream: list[int], bit_time_ns: float = 0.0) -> bool:
        """
        Send a pre-stuffed bitstream. Handles arbitration loss gracefully.
        
        Returns:
            True if the entire frame was transmitted successfully.
            False if arbitration was lost mid-frame.
        """
        self.arbitration_lost = False
        self.lost_at_bit_index = -1
        
        for i, bit in enumerate(bitstream):
            success = await self.bus.drive_bit(self.node_id, bit, bit_time_ns)
            if not success:
                self.arbitration_lost = True
                self.lost_at_bit_index = i
                # In real hardware, the node would switch to receiver mode here.
                # For our model, returning False is sufficient to halt transmission.
                return False
                
        return True
