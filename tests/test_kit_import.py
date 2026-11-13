import pytest
import canfd_kit
from canfd_kit.bus.canfd_bus import CANFDDriver, CANFDMonitor

def test_package_version():
    assert canfd_kit.__version__ == "0.2.0-dev"

def test_classes_exist():
    assert CANFDDriver is not None
    assert CANFDMonitor is not None
