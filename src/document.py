import ast
import openai
import re
import os
import time
import dotenv

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_KEY")
import ast


def extract_functions(file_path, exclude_docstrings=True):
    """
    Extracts all functions from a Python file and returns a list of objects containing information on the function signature and body.

    Args:
        file_path (str): The path to the Python file to extract functions from.
        exclude_docstrings (bool, optional): If True, excludes functions that have docstrings. Defaults to True.

    Returns:
        list: A list of `ast.FunctionDef` objects representing each function found in the file.

    The function opens the Python file at the specified path, parses it, and then returns a list of `ast.FunctionDef` objects for each function in the file. If the `exclude_docstrings` argument is set to True (default), functions with docstrings will be excluded from the returned list. This function leverages the Abstract Syntax Trees (AST) library to parse the Python source code.

    Note that this function does not execute or import the Python code in any way nor any direct interaction with the underlying Operating System's files beyond opening the requested file with read
    """
    "\nExtracts all functions from a Python file and returns a list of objects containing information on the function signature and body.\n\nArgs:\n    file_path (str): The path to the Python file to extract functions from.\n    exclude_docstrings (bool, optional): If True, excludes functions that have docstrings. Defaults to True.\nReturns:\n    list: A list of `ast.FunctionDef` objects representing each function found in the file.\n"
    "\n    Extracts all functions from a Python file and returns a list of objects\n    containing information on the function signature and body.\n    "
    with open(file_path, "r") as file:
        source = file.read()
    module = ast.parse(source)
    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    if exclude_docstrings:
        functions = [
            function for function in functions if not ast.get_docstring(function)
        ]
    return functions


def generate_docstring(function_string: str, attempts=0):
    """
    Generates a docstring for a given function signature and description using the OpenAI GPT-3 API. The function takes in a function signature and a description as input, and returns a docstring that follows PEP conventions. The docstring includes a summary line, followed by a blank line and a more elaborate description. It documents the function's behavior, arguments, return values, side effects, exceptions raised, and restrictions on when it can be called. Optional arguments are indicated. It is documented whether keyword arguments are part of the interface. The function makes use of the OpenAI GPT-3 API and returns the generated docstring.
    """
    "\nGenerates a docstring for a given function signature and description using the OpenAI GPT-3 API. The function takes in a function signature and a description as input, and returns a docstring that follows PEP conventions. The docstring includes a summary line, followed by a blank line and a more elaborate description. It also documents the function's behavior, arguments, return values, side effects, exceptions raised, and restrictions on when it can be called. The function makes use of the OpenAI GPT-3 API and returns the generated docstring. \n"
    "\n    Generates a docstring for a given function signature and description\n    using the OpenAI GPT-3 API.\n    "
    docstring_prompt = f'\n    Your responses should follow PEP conventions.\n    A good docstring consist of a summary line just like a one-line docstring, followed by a blank line, followed by a more elaborate description.\n    The docstring for a function or method should summarize its behavior and document its arguments, return value(s), side effects, exceptions raised, and restrictions on when it can be called (all if applicable). Optional arguments should be indicated. It should be documented whether keyword arguments are part of the interface.\n    Lines over 80 characters should be broken into a new line using a \n character.\n    A docstring should always start with """ and should always end with """.\n    Here is an example of a simple function with a good docstring:\n    def complex(real=0.0, imag=0.0):\n        """Form a complex number.\n\n        Keyword arguments:\n        real -- the real part (default 0.0)\n        imag -- the imaginary part (default 0.0)\n        """\n        if imag == 0.0 and real == 0.0:\n            return complex_zero\n    '
    prompt = f'\n    Generate a concise but informative docstring for the following function. You should just return the docstring and nothing else. Your reponse should always begin with """ and always end with """ Function:\n\n{function_string}\n\n \n    '
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert programmer with 20+ years of experience writing clean and efficient Python code. You are particularly well versed in PEP style conventions and writing good documentation.",
                },
                {"role": "system", "content": docstring_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
        )
    except openai.error.APIError as e:
        if attempts > 3:
            raise e
        return generate_docstring(function_string, attempts + 1)
    except ConnectionResetError as e:
        if attempts > 3:
            raise e
        return generate_docstring(function_string, attempts + 1)
    except openai.error.RateLimitError as e:
        if attempts > 3:
            raise e
        print("Hit rate limit. Waiting 20 seconds")
        time.sleep(21)
        return generate_docstring(function_string, attempts + 1)
    return response.choices[0].message.content


def add_docstring(function: ast.FunctionDef) -> ast.FunctionDef:
    """The `add_docstring` function adds or updates the docstring for a given function using PEP conventions. It takes an ast.FunctionDef object representation of the function to add or update the docstring for. The function returns the ast.FunctionDef object with its docstring added or updated according to PEP conventions. If the docstring for the function exists, the function will replace it. If it does not exist, the function will add it."""
    "\nAdd or update the docstring for a given function using PEP conventions.\n\nArguments:\nfunction -- The ast.FunctionDef object representation of the function to add/update the docstring for.\n\nReturns:\nThe ast.FunctionDef object with its docstring added/updated according to PEP conventions.\n"
    docstring = generate_docstring(ast.unparse(function))
    if docstring[:3] != '"""':
        docstring = '"""' + docstring
    if docstring[-3:] != '"""':
        docstring += '"""'
    function.body.insert(0, ast.parse(docstring).body[0])
    return function


def add_docstrings_to_file(file_path):
    """Adds docstrings to all functions in a file.

    Keyword arguments:
    file_path -- the path of the file (must be a valid Python file)"""
    "\nAdds docstrings to all functions in a file.\n    \nKeyword arguments:\nfile_path -- the path of the file (must be a valid Python file)\n"
    "\n    Adds docstrings to all functions in a file.\n    "
    functions = extract_functions(file_path)
    for function in functions:
        print(function.name)
        function = add_docstring(function)
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


import os
import fnmatch


def process_directory(directory_path):
    """
    Add docstrings to all functions and classes in Python files within the specified directory.

    Args:
        directory_path (str): Path of the directory where the Python files are located.

    Returns:
        None.

    The function processes each file in the specified directory and adds docstrings to all functions and classes contained within. The function checks if the file has a valid Python file extension and if it doesn't contain any dunder (__) characters in the filename. Once a valid file is identified, it proceeds to call the 'add_docstrings_to_file' function to add docstrings to each function and class contained within the file. The function does not return any values.
    """
    "\nAdd docstrings to all functions and classes in python files within a specified directory.\n\nArgs:\ndirectory_path (str): Path of the directory where the python files are located.\n\nReturns:\nNone\n"
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            if fnmatch.fnmatch(file_name, "*.py"):
                if "__" not in file_name:
                    file_path = os.path.join(root, file_name)
                    add_docstrings_to_file(file_path)


if __name__ == "__main__":
    PATH = "/Users/landon/Projects/cheffrey/src"
    process_directory(PATH)
