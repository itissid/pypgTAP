# The null handler at the top level name space
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
