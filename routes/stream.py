import   os
import   time


def loadTemplate(name, title, delim='<div class="content">'):

    try:
        dr = os.path.join(".", "templates")
        fn = os.path.join(dr, f"{name}.html" )

        with open(fn, encoding="utf-8") as inFile:
            strContents = inFile.read()
            print(f"loaded template '{name:12}' - {len(strContents):3} ")

            strContents = strContents.replace(
                """<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">""", 
                " ",
            )
            strContents = strContents.replace(
                """{{ HTMLTitle    |safe }}""", 
                title,
            )

            parts = strContents.split(delim)
            return parts[0]

    except Exception as exc:
        print(str(exc))
        return str(exc)

mainTplP1 = loadTemplate("main","stream")

bodySuffix = """
    </div>
</body>
</html>
"""

# a generator, yielding chunks of data
def generate():
    yield mainTplP1
    yield "<p>Starting streaming...</p>\n" + " " * 1024  # Force an early flush with padding    
    yield f"<div style='height: 2px; background-color: grey'> { '&nbsp;'  * 1024} </div>"  # Force an early flush with padding    
    for i in range(8):
        yield f"<p>Chunk {(i + 1):2}</p>\n"  # Send the chunk to the client
        time.sleep(0.15)  # Simulate a delay (e.g., long-running process)
    yield f"<p>response finished</p>\n" 
    yield bodySuffix 


    
