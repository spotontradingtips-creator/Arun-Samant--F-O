
import logging
import pytz
from datetime import datetime
import pandas as pd

logger = logging.getLogger("rich")

class IntegrityShield:
    """
    Project Titan-Shield: Cross-source ground-truth verification engine.
    Ensures that the primary broker data is not 'poisoned' or stale
    by comparing it against secondary sources.
    """
    @staticmethod
    def verify_indicator_integrity(underlying, broker_val, source_val, name, threshold=1.0):
        """
        Compare broker indicator against ground truth source.
        """
        delta = abs(broker_val - source_val)
        if delta > threshold:
            logger.critical(f"[SHIELD] {underlying} {name} POISONED! Broker={broker_val:.2f}, Source={source_val:.2f}, Delta={delta:.2f} (Limit={threshold})")
            return False
            
        logger.info(f"[SHIELD] {underlying} {name} Integrity: PASS (Delta={delta:.2f})")
        return True

    @staticmethod
    def manifest_handshake(config_val, manifest_val, rule_name):
        """
        Verify that Live Config matches the Neural Manifest textbook.
        """
        if float(config_val) != float(manifest_val):
            logger.critical(f"[SHIELD] TEXTBOOK DISCREPANCY! {rule_name}: Config={config_val}, Manifest={manifest_val}")
            return False
        return True
