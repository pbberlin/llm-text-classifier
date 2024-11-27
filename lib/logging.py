import asyncio
import functools
import logging
import time


lg = logging.getLogger("llm.toolbox")

logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s - %(levelname)s - %(message)s",
    format="%(levelname)s:\t%(message)s",
)


# customize main logger
lg2 = logging.getLogger("uvicorn.access")

class FilterStaticRequests(logging.Filter):
    def filter(self, record):
        # filter out favicon.ico and static images
        c1 = "favicon.ico" not in record.getMessage()
        c2 = "static/img"  not in record.getMessage()
        c3 = "static/css"  not in record.getMessage()
        c4 = "static/js"   not in record.getMessage()
        return c1 and c2 and c3 and c4

lg2.addFilter(FilterStaticRequests())



# profile af function
def prof(func):
    """decorator - for execution time of func"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        strt = time.perf_counter()
        rslt = await func(*args, **kwargs)
        stop = time.perf_counter()
        lg.info(f"\tfunc {func.__name__!r} executed in {stop - strt:.4f}s")
        return rslt

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        strt = time.perf_counter()
        rslt = func(*args, **kwargs)
        stop = time.perf_counter()
        lg.info(f"\tfunc {func.__name__!r} executed in {stop - strt:.4f}s")
        return rslt

    # wrap sync and async - accordingly
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
