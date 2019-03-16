import difflib


with open('test') as f1:
    mergecontent = f1.readlines()
with open('file') as f2:
    curcontent = f2.readlines()
print(curcontent)
print(mergecontent)
d = difflib.SequenceMatcher(None, curcontent, mergecontent)
diff = d.get_opcodes()
a = difflib.ndiff(curcontent, mergecontent)
print(''.join(a))
print(list(diff))
