from spx.spxobjects.spxSnippet import spxSnippet

sn = spxSnippet()
sn.content = '<iframe>plop</iframe><pre>tototata</pre>'
sn.stripXSS()
sn.encrypt()

print(sn.content)

print(sn.decrypt(sn.clearKey))

print(sn.content)
