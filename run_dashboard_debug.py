#!/usr/bin/env python
"""
Debug version of the dashboard to troubleshoot button clicks.
"""
import sys
sys.path.insert(0, 'src')

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from candle_patterns.dashboard import app

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("STARTING DASHBOARD IN DEBUG MODE")
    logger.info("=" * 60)
    logger.info("Listen on http://127.0.0.1:8050")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    # Run with threading to see callback logs
    app.run(
        debug=True,
        host='127.0.0.1',
        port=8050,
        use_reloader=False,
        threaded=True
    )
