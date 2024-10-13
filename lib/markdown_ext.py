import markdown


markDn = '''
### Analyze any speech or text against above statements

* Take any Lagarde speech or any other text and benchmark it against your statements above.
* Input speech is benchmarked sentence by sentence.
* Investigate: Larger chunks. Larger context.
* Investigate: Thin    corpus data leading to hallucinations.
* Investigate: Slanted corpus data leading to hallucinations.
'''
markDn   = markdown.markdown(markDn)
