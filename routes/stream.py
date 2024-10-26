import   time

from lib.util import mainTemplateHeadForChunking, templateSuffix


def chunksGenerator():
    yield mainTemplateHeadForChunking("main","stream")
    yield "<p>Starting streaming...</p>\n" + " " * 1024  # Force an early flush with padding
    yield f"<div style='height: 2px; background-color: grey'> { '&nbsp;'  * 1024} </div>"  # Force an early flush with padding
    for i in range(8):
        yield f"<p>Chunk {(i + 1):2}</p>\n"  # Send the chunk to the client
        time.sleep(0.15)  # Simulate a delay (e.g., long-running process)
    yield f"<p>response finished</p>\n"
    yield templateSuffix()






