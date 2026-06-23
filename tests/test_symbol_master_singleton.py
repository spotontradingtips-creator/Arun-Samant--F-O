"""Tests for SymbolMaster singleton thread safety"""

import pytest
import threading
from src.symbol_master import SymbolMaster


class TestSymbolMasterSingleton:
    """Test that SymbolMaster is properly singleton-enforced"""

    def test_single_instance_creation(self):
        """Test that multiple instantiations return the same object"""
        instance1 = SymbolMaster()
        instance2 = SymbolMaster()
        instance3 = SymbolMaster()

        assert instance1 is instance2, "Instances should be the same object"
        assert instance2 is instance3, "Instances should be the same object"
        assert id(instance1) == id(instance2) == id(instance3), "IDs should match"

    def test_singleton_with_concurrent_access(self):
        """Test that singleton works correctly under concurrent access"""
        instances = []
        lock = threading.Lock()

        def create_instance():
            sm = SymbolMaster()
            with lock:
                instances.append(sm)

        # Create 10 threads trying to instantiate SymbolMaster
        threads = [threading.Thread(target=create_instance) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All instances should be the same object
        assert len(instances) == 10, "Should create 10 instances"
        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance, "All instances should be the same singleton"

    def test_singleton_initialization_once(self):
        """Test that __init__ is only called once across instances"""
        # Reset singleton state for testing
        SymbolMaster._instance = None

        # Track how many times load_master is called
        load_count = {"count": 0}
        original_load_master = SymbolMaster.load_master

        def mock_load_master(self, filepath="nfo_master.csv"):
            load_count["count"] += 1

        SymbolMaster.load_master = mock_load_master

        try:
            instance1 = SymbolMaster()
            instance2 = SymbolMaster()
            instance3 = SymbolMaster()

            # load_master should be called only once
            assert load_count["count"] == 1, "load_master should only be called once"
            assert instance1 is instance2 is instance3, "Should be same instance"

        finally:
            # Restore original method and reset singleton
            SymbolMaster.load_master = original_load_master
            SymbolMaster._instance = None

    def test_singleton_state_persistence(self):
        """Test that state is preserved across different references"""
        SymbolMaster._instance = None

        instance1 = SymbolMaster()
        # Modify state
        instance1.test_attribute = "test_value"

        instance2 = SymbolMaster()
        # Should see the same attribute on the second reference
        assert hasattr(instance2, "test_attribute"), "State should persist"
        assert instance2.test_attribute == "test_value", "State should be preserved"

        # Reset for cleanup
        SymbolMaster._instance = None

    def test_singleton_attributes_shared(self):
        """Test that all attributes are shared across references"""
        SymbolMaster._instance = None

        instance1 = SymbolMaster()
        instance1.custom_data = {"key": "value"}

        instance2 = SymbolMaster()
        instance2.custom_data["key"] = "modified_value"

        # Both instances should reflect the change
        assert instance1.custom_data["key"] == "modified_value", "Modifications should be visible"
        assert instance2.custom_data["key"] == "modified_value", "Modifications should be visible"

        # Reset for cleanup
        SymbolMaster._instance = None

    def test_concurrent_reads(self):
        """Test that concurrent reads don't cause issues"""
        SymbolMaster._instance = None

        instance = SymbolMaster()
        results = []
        lock = threading.Lock()

        def read_data():
            # Try to read singleton data
            sm = SymbolMaster()
            with lock:
                results.append(sm is instance)

        threads = [threading.Thread(target=read_data) for _ in range(20)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All reads should return the same instance
        assert all(results), "All concurrent reads should get the same instance"
        assert len(results) == 20, "Should process all requests"

        # Reset for cleanup
        SymbolMaster._instance = None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
