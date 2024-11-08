# second doc

<!--h-->

## High level

* foo
* bar
* => Inspiration

<!--h-->


#### UML 1


<div class="mermaid">
graph TB
A --> Ba
B --> C
</div>


#### UML 2


<div class="mermaid">
sequenceDiagram
autonumber
Alice->>John: Hello John, how are you?
loop Healthcheck
John->>John: Fight against hypochondria
end
Note right of John: Rational thoughts!
John-->>Alice: Great!
John->>Bob: How about you?
Bob-->>John: Jolly good!
</div>


<script src="../../static/dist/mermaid/mermaid.min.js"></script>
<script>
    document.addEventListener("DOMContentLoaded", function () {
        mermaid.initialize({ startOnLoad: true });
        console.log("mermaid init success");
    });
    // mermaid.initialize({ theme: "dark", startOnLoad: true });
    // mermaid.render() // to render specific diagrams
</script>
