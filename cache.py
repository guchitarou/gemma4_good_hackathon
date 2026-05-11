import diskcache
from dash import DiskcacheManager

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)