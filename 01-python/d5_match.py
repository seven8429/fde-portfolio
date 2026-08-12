#match like if
#if
_if = 'hi'
if _if == 'hi':
    print('hi')
elif _if == 'hello':
    print('hello')
else:
    print('bye')
#match
match _if:
    case 'hi':
        print('hi')
    case 'hello':
        print('hello')
    case _:
        print('bye')

args = ['gcc', 'hello.c', 'world.c']
# args = ['clean']
# args = ['gcc']

match args:
    # 如果仅出现gcc，报错:
    case ['gcc']:
        print('gcc: missing source file(s).')
    # 出现gcc，且至少指定了一个文件:
    case ['gcc', file1, *files]:
        print('gcc compile: ' + file1 + ', ' + ', '.join(files))
    # 仅出现clean:
    case ['clean']:
        print('clean')
    case _:
        print('invalid command.')