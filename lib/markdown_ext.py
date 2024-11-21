import markdown
import re




markDn = '''
### Analyze any speech or text against above statements

* Take any Lagarde speech or any other text and benchmark it against your statements above.
* Input speech is benchmarked sentence by sentence.
* Investigate: Larger chunks. Larger context.
* Investigate: Thin    corpus data leading to hallucinations.
* Investigate: Slanted corpus data leading to hallucinations.
'''
markDn   = markdown.markdown(markDn)




#                       two spaces
#                              end of line
RE_MD_WRAP = re.compile(r'[ ]{2,3}\r?\n')    # LF or CRLF
def markdownLineWrap(s: str):
    return RE_MD_WRAP.sub("<br>\n", s )


def splitByMarkownHeaders(s: str, hdrLvl: int):

    # LF or CRLF - optional trailing white space -
    #    x times '#' followed by space

    tpl = r'\r?\n[\s]{0,3}[#]{2}[\s]+'
    tpl = r'\r?\n[\s]{0,3}[#]{    2              }[\s]+'
    eff = r'\r?\n[\s]{0,3}[#]{'+ str(hdrLvl) + r'}[\s]+'

    RE_SECTION = re.compile(eff)
    parts = RE_SECTION.split(s)
    print(f"\tfound {len(parts)-1:2} headers of level {hdrLvl} => {len(parts)} parts")
    return parts



RE_LINEBREAK = re.compile(r'\r?\n')    # LF or CRLF
def splitByLineBreak(s: str):
    # lines = RE_LINEBREAK.split(s)
    lines = s.splitlines()
    return lines



'''
    Page break for every header 1-3
        # Heading 1
        ## Heading 2...

    In addition: Explicit page break can be set using
        <!--pagebreak-->

'''
def renderToRevealHTML(mdContent):

    pbInner = "<!--pagebreak-->"
    pbOuter = f"\r\n{pbInner}\r\n"

    # wrapping into <section> tags _after_ conversion to HTML proved impossible:
    # found no comfy document tree parser to wrap subtrees into <section>.
    # Instead we insert user-defined string <!--pagebreak--> before headings.
    # <!--pagebreak--> can be inserted in original markdown too.
    for hdrLvl in [2,3,4]:
        sections = splitByMarkownHeaders(mdContent, hdrLvl)
        mdContent = f"{pbOuter}{ '#'*hdrLvl } ".join(sections)


    if False:
        # auto split long text without headings
        splitThreshold = 12
        sections = mdContent.split(pbInner)
        for idx1, sect in enumerate(sections):
            lines = splitByLineBreak(sect)
            nonEmpty =  [ln for ln in lines if ln]

            if len(nonEmpty) > splitThreshold:
                linesNew = []
                lastInsert = 0
                for idx2, line in enumerate(lines):
                    if lastInsert > splitThreshold:
                        if not line.startswith(" "):
                            lastInsert = 0
                            linesNew.append("\r\n<!-- automatic pagebreak insertion -->")
                            linesNew.append(pbOuter)
                            print(f"\tsect{idx1} - pb before after {idx2}")
                    linesNew.append(line)
                    lastInsert += 1
                sections[idx1] = "\n".join(linesNew)

        mdContent = pbOuter.join(sections)

    mdContent = markdownLineWrap(mdContent)


    # https://python-markdown.github.io/extensions/
    # https://python-markdown.github.io/extensions/attr_list/
    # we can add CSS classes, element IDs and key-value attributes to markdown
    # using syntax   {: #myid .myclass   key='val' }
    from markdown.extensions.attr_list import AttrListExtension

    # note: dont use the mermaid extension
    #   instead write mermaid elements as <div class="mermaid">...
    #   and import the necessary javascript.
    #   examples in doc2.md

    htmlContent = markdown.markdown(
        mdContent,
        extensions=[AttrListExtension()],
        extension_configs="",
        tab_length=4,
    )


    # replacing  <!--pagebreak--> from above
    #  turning it into <section> nodes
    openSect = "\t<section>\n"
    closSect = "\n\t</section>"

    # replace inner
    htmlContent = htmlContent.replace( pbInner, f"{closSect}{openSect}")
    # enclose outer
    htmlContent = f"{openSect}<!--outer-->\n{htmlContent}\n<!--outer-->{closSect}"

    '''
     negative: ol counter will now be reset across sections.
      How do we preserve order list numbers across sections?
        	<ol start="3"> ?
      Using attr_list extension - we manually insert
           {: start='3' }
      Remember: separate line after markdown element
      But documentation says 'implied elements ... ul, ol ... no way'
      We have to set an explicit value with each li:

        3.  content of list item 3
        {: value='3' }
            * sub-list 1
        4.  content of list item 4
        {: value='4' }
            * sub-list 1
            * sub-list 2


          '''


    # there might be <p> and <p key=val>
    htmlContent = htmlContent.replace("<p ",   '<p class="fragment" ')
    htmlContent = htmlContent.replace("<p>",   '<p class="fragment" >')

    htmlContent = htmlContent.replace("<li class=\"", '<li  class="fragment ')  # two spaces - to prevent subsequent
    # htmlContent = htmlContent.replace("<li ", '<li class="fragment" ')
    htmlContent = htmlContent.replace("<li>", '<li class="fragment" >')

    htmlContent = htmlContent.replace("<tr ", '<tr class="fragment" ')
    htmlContent = htmlContent.replace("<tr>", '<tr class="fragment" >')

    htmlContent = htmlContent.replace("<blockquote ", '<blockquote class="fragment" ')
    htmlContent = htmlContent.replace("<blockquote>", '<blockquote class="fragment" >')

    if False:
        # images always inside list items
        htmlContent = htmlContent.replace("<img ", '<img class="fragment" ')

    # htmlContent = htmlContent.replace("<blockquote class=\"", '<blockquote class="fragment ')

    #  src="./img/xyz.jpg
    #       to
    #  src="/img/doc/xyz.jpg

    # image handler for doc
    htmlContent = htmlContent.replace("src=\"./img/", "src=\"/doc/img/")

    return htmlContent
