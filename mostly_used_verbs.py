import ast
import os
import collections
from nltk import pos_tag


def flat(lst):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in lst], [])


def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'

def is_magical(f):

    return f.startswith('__') and f.endswith('__')


def is_py_file(path, max_length):
    filenames = []
    for dirname, dirs, files in os.walk(path, topdown=True):
        if len(filenames) >= max_length:
            break
        else:
            py_files = file_filtering(files, dirname, formatting=".py")
        filenames.extend(py_files)
    print('total %s files' % len(filenames))
    return filenames

def file_filtering(files, dirname, formatting):
    return [os.path.join(dirname, f) for f in files if f.endswith(formatting)]


def get_trees(path, with_filenames=False, with_file_content=False):

    """
    Returns the trees list including every file tree
    """
    trees = []
    filenames = is_py_file(path, max_length= 100)
    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
        try:
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None
        if with_filenames:
            if with_file_content:
                trees.append((filename, main_file_content, tree))
            else:
                trees.append((filename, tree))
        else:
            trees.append(tree)
    print('trees generated')
    return trees

def get_verbs_from_function_name(function_name):
    return [word for word in function_name.split('_') if is_verb(word)]


def get_top_verbs_in_path(path, top_size=10):
    #Returns a list of top_size = 10 elements
    trees = [t for t in get_trees(path) if t]
    functions = [f for f in flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in trees]) if not is_magical(f)]
    print('functions extracted')
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in functions])
    return collections.Counter(verbs).most_common(top_size)

words = []
projects = [
    'django',
    'flask',
    'pyramid',
    'reddit',
    'requests',
    'sqlalchemy'
]
for project in projects:
    path = os.path.join('.', project)
    words += get_top_verbs_in_path(path)

top_size = 200
print('total %s words, %s unique' % (len(words), len(set(words))))
for word, occurence in collections.Counter(words).most_common(top_size):
    print(word, occurence)
