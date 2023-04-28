import ast
import openai
import re
import os
import time
openai.api_key = os.getenv('OPENAI_KEY')



file_path = './cheffrey.py'
import ast

def extract_functions(file_path, exclude_docstrings = True):
    """
    Extracts all functions from a Python file and returns a list of objects
    containing information on the function signature and body.
    """
    with open(file_path, "r") as file:
        source = file.read()
    module = ast.parse(source)

    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    if exclude_docstrings:
        functions = [function for function in functions if not ast.get_docstring(function)]
    
    return functions

def generate_docstring(function_string: str, attempts = 0):
    """
    Generates a docstring for a given function signature and description
    using the OpenAI GPT-3 API.
    """
    docstring_prompt = f'''
    Your responses should follow PEP conventions.
    A good docstring consist of a summary line just like a one-line docstring, followed by a blank line, followed by a more elaborate description.
    The docstring for a function or method should summarize its behavior and document its arguments, return value(s), side effects, exceptions raised, and restrictions on when it can be called (all if applicable). Optional arguments should be indicated. It should be documented whether keyword arguments are part of the interface.
    Lines over 80 characters should be broken into a new line using a \n character.
    Here is an example of a simple function with a good docstring:
    def complex(real=0.0, imag=0.0):
        """Form a complex number.

        Keyword arguments:
        real -- the real part (default 0.0)
        imag -- the imaginary part (default 0.0)
        """
        if imag == 0.0 and real == 0.0:
            return complex_zero
    '''
    prompt = f"""
    Generate a concise but informative docstring for the following function. You should just return the docstring and nothing else. Function:\n\n{function_string}\n\n 
    """

    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo', 
            messages = [
                {'role': 'system', 'content': 'You are an expert programmer with 20+ years of experience writing clean and efficient Python code. You are particularly well versed in PEP style conventions and writing good documentation.'},
                {'role': 'system', 'content': docstring_prompt},
                {'role': 'user', 'content': prompt}
            ], 
            max_tokens = 200)
    except openai.error.APIError as e:
        if attempts > 3:
            raise e
        return generate_docstring(function_string, attempts+1)
    except ConnectionResetError as e:
        if attempts > 3:
            raise e
        return generate_docstring(function_string, attempts+1)
    except openai.error.RateLimitError as e:
        if attempts > 3:
            raise e
        print('Hit rate limit. Waiting 20 seconds')
        time.sleep(21)
        return generate_docstring(function_string, attempts+1)
    return response.choices[0].message.content


def add_docstring(function: ast.FunctionDef)->ast.FunctionDef:
    docstring = generate_docstring(ast.unparse(function))
    function.body.insert(0, ast.parse(docstring).body[0])
    return function

def add_docstrings_to_file(file_path):
    """
    Adds docstrings to all functions in a file.
    """
    # Extract functions from file
    functions = extract_functions(file_path)

    # Add docstrings to each function
    for function in functions:
        print(function.name)
        function = add_docstring(function)

    # Rewrite file with modified functions
    with open(file_path, "r+") as file:
        source = file.read()
        module = ast.parse(source)
        ast.fix_missing_locations(module)
        for i, node in enumerate(module.body):
            if isinstance(node, ast.FunctionDef):
                module.body[i] = add_docstring(node)
        file.seek(0)
        file.write(ast.unparse(module))
        file.truncate()
    
def parse_python_file(file_path):
    """
    Parses a Python file and extracts information about the functions and
    non-function code using the ast module. Generates docstrings for each
    function using the OpenAI GPT-3 API.
    """
    with open(file_path, 'r') as f:
        file_contents = f.read()
    module = ast.parse(file_contents)

    class FunctionVisitor(ast.NodeVisitor):

        def __init__(self):
            self.functions = []

        def visit_FunctionDef(self, node):
            function_name = node.name
            # parameters = ast.get_args(node.args)
            parameters_str = ast.unparse(node.args)
            description = ''
            for item in node.body:
                if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant) and isinstance(item.value.value, str):
                    description = item.value.value
                    break
            signature = f'def {function_name}{parameters_str}:'
            print(signature)
            print(description)
            raise ValueError('Stop')
            docstring = generate_docstring(signature, description)
            self.functions.append({'name': function_name, 'parameters': parameters_str, 'docstring': docstring, 'lineno': node.lineno})

    class NonFunctionVisitor(ast.NodeVisitor):

        def __init__(self):
            self.lines = []

        def visit(self, node):
            if isinstance(node, ast.FunctionDef):
                return
            line = file_contents[node.lineno - 1:node.end_lineno]
            line = re.sub('\\s+', ' ', line.strip())
            self.lines.append({'code': line, 'lineno': node.lineno})
    function_visitor = FunctionVisitor()
    function_visitor.visit(module)
    nonfunction_visitor = NonFunctionVisitor()
    nonfunction_visitor.visit(module)
    return {'functions': function_visitor.functions, 'nonfunctions': nonfunction_visitor.lines}

def save_documentation(file_path):
    print(f'Working on : {file_path}')
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    class DocstringTransformer(ast.NodeTransformer):

        def visit_FunctionDef(self, node):
            if not node.body or not isinstance(node.body[0], ast.Expr) or (not isinstance(node.body[0].value, ast.Str)):
                signature = ast.get_source_segment(node.args).strip()
                description = node.name
                docstring = generate_docstring(signature, description)
                node.body = [ast.Expr(ast.Str(docstring))] + node.body
            return node

        def visit(self, node):
            if not isinstance(node, ast.FunctionDef):
                if not hasattr(node, 'lineno'):
                    return node
                comment = ast.Comment('TODO: Add documentation')
                comment.lineno = node.lineno
                comment.col_offset = 0
                return [comment, node]
            return node
    transformer = DocstringTransformer()
    new_tree = transformer.visit(tree)
    with open(file_path, 'w') as f:
        f.write(ast.unparse(new_tree))
import os
import fnmatch

def process_directory(directory_path):
    for (root, dirs, files) in os.walk(directory_path):
        for file_name in files:
            if fnmatch.fnmatch(file_name, '*.py'):
                if '__' not in file_name:
                    file_path = os.path.join(root, file_name)
                    save_documentation(file_path)
if __name__ == '__main__':
    PATH = '/Users/landon/Projects/cheffrey/src'
    process_directory(PATH)