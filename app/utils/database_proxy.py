import logging
from datetime import datetime
from typing import Optional

class DatabaseProxy:
    """Proxy for controlling access to password viewing and logging attempts"""
    
    def __init__(self, db_manager):
        self._db_manager = db_manager
        logging.basicConfig(filename='access.log', level=logging.INFO)

    def get_password(self, row_id: int) -> Optional[str]:
        """Proxy method to get password with access logging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            password = self._db_manager.get_password(row_id)
            if password:
                logging.info(f"{timestamp}: Password viewed successfully for ID {row_id}")
                return password
            else:
                logging.warning(f"{timestamp}: Failed to retrieve password for ID {row_id}")
                return None
        except Exception as e:
            logging.error(f"{timestamp}: Error retrieving password for ID {row_id}: {str(e)}")
            return None