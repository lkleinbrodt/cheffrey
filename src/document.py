import ast
import openai
import re
import os
import time
import dotenv
import subprocess

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_KEY")
import ast


def extract_functions(file_path, exclude_docstrings=True):
    """Extracts all functions from a Python file and returns a list of `ast.FunctionDef` objects.

    Args:
        file_path (str): The path to the Python file to extract functions from.
        exclude_docstrings (bool, optional): If True, excludes functions with docstrings. Defaults to True.

    Returns:
        list: A list of `ast.FunctionDef` objects representing each function found in the file.

    This function opens a Python file, parses it using the Abstract Syntax Trees (AST) library and returns a list of `ast.FunctionDef` objects, which contain information about the function signature and body. If `exclude_docstrings` is True (default), functions with docstrings will be excluded from the returned list. This function does not execute or import the Python code.
    """
    "\n    Extracts all functions from a Python file and returns a list of objects containing information on the function signature and body.\n\n    Args:\n        file_path (str): The path to the Python file to extract functions from.\n        exclude_docstrings (bool, optional): If True, excludes functions that have docstrings. Defaults to True.\n\n    Returns:\n        list: A list of `ast.FunctionDef` objects representing each function found in the file.\n\n    This function opens a Python file specified by `file_path`, parses it using the Abstract Syntax Trees (AST) library and returns a list of `ast.FunctionDef` objects for each function found in the file. If the `exclude_docstrings` argument is set to True (default), functions with docstrings will be excluded from the returned list.\n    Note that this function does not execute or import the Python code.\n    "
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
    """Generate a PEP-compliant docstring for the given function. The function accepts a string representation of a function and returns a string representing the docstring for that function. The function calls GPT-3 to generate the docstring based on a prompt it generates. The prompt includes definitions of a good docstring and a sample function with a docstring to follow. The function will continuously call GPT-3 until an output is generated. The generated docstring should concisely summarize the function, document its arguments, return value(s), side effects, exceptions raised, and restrictions on when it can be called (if applicable)."""
    docstring_prompt = f'Your responses should follow PEP conventions.\n    A good docstring consists of a summary line just like a one-line docstring, followed by a blank line, followed by a more elaborate description.\n    The docstring for a function or method should summarize its behavior and document its arguments, return value(s), side effects, exceptions raised, and restrictions on when it can be called (all if applicable).\n    Here is an example of a simple function with a good docstring:\n    def complex(real=0.0, imag=0.0):\n        """Form a complex number.\n\n        Keyword arguments:\n        real -- the real part (default 0.0)\n        imag -- the imaginary part (default 0.0)\n        \n        if imag == 0.0 and real == 0.0:\n            return complex_zero"""\n'
    prompt = f'Generate a concise but informative docstring for the following function. You should just return the docstring and nothing else. Do not be overly verbose. Your reponse must always begin with """ and always end with """ on a new line. Function:\n\n{function_string}\n\n \n    '
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert programmer with 20+ years of experience writing clean and efficient Python code. You like to write clean, concise code and documentation.",
                },
                {"role": "system", "content": docstring_prompt},
                {
                    "role": "system",
                    "content": 'Short and simple functions only need a one-liner docstring. Lines over 80 characters should be broken into a new line. Your response MUST ALWAYS start with """ and MUST ALWAYS end with """ on a new line',
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
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


def add_docstring(function: ast.FunctionDef, is_retry=False) -> ast.FunctionDef:
    """Adds a docstring to the given AST function definition.

    Args:
        function (ast.FunctionDef): AST function definition needing a docstring.

    Returns:
        ast.FunctionDef: The input function definition with an added docstring.

    The function takes an AST function definition and adds a docstring to its starting lines. If a docstring already exists, the current one is replaced with a new one. If no parsed expression is in the newly generated docstring, the function raises a SyntaxError.

    Note: if the function definition contains quotes, the resultant docstring may have quote escape characters.
    """

    docstring = generate_docstring(ast.unparse(function))
    try:
        parsed_docstring = ast.parse(docstring).body[0]
        function.body.insert(0, parsed_docstring)
    except SyntaxError as e:
        if is_retry:
            print(docstring)
            raise e
        else:
            return add_docstring(function, is_retry=True)
    return function


def add_docstrings_to_file(file_path, format=True):
    """Add docstrings to all the functions in a python code file and update the file.

    file_path: directory path of the python file
    format: whether to format the code using black (default=True)

    This function takes in the path of a python code file and adds docstrings to all the functions available in the file. By using the abstract syntax tree module(ast) this function replaces the specified function definition with its docstring. The updated file is written back to the original filename with a formatted file(using black format) if format argument is True.
    Returns None"""
    print(file_path)
    with open(file_path, "r+") as file:
        source = file.read()
        module = ast.parse(source)
        ast.fix_missing_locations(module)
        for i, node in enumerate(module.body):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(function):
                    if "__" not in node.name:
                        print("\t", node.name)
                        module.body[i] = add_docstring(node)
        file.seek(0)
        file.write(ast.unparse(module))
        file.truncate()
    if format:
        subprocess.run(["black", file_path], capture_output=True, check=True, text=True)


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

    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            if fnmatch.fnmatch(file_name, "*.py"):
                if "__" not in file_name:
                    file_path = os.path.join(root, file_name)
                    add_docstrings_to_file(file_path)


if __name__ == "__main__":
    PATH = "/Users/landon/Projects/cheffrey/src"
    process_directory(PATH)
