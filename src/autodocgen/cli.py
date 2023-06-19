import argparse
import logging
import os
import time
from pathlib import Path
from tqdm import tqdm
from autodocgen.ast_analyzer import ASTAnalyzer
from autodocgen.file_visitor import FileVisitor


def path_walk(directory: Path) -> tuple[list[Path], list[Path]]:
    """
    Return a tuple containing two lists of Path objects representing directories and
     files in a given directory and its subdirectories.

    :param directory: A Path object representing the directory to walk.
    :type directory: Path
    :return: A tuple containing two lists of Path objects representing directories and files.
    :rtype: tuple[list[Path], list[Path]]"""
    for root, dirs, files in os.walk(directory):
        root_path = Path(root)
        dir_paths = [root_path / d for d in dirs]
        file_paths = [root_path / f for f in files]
        yield (dir_paths, file_paths)


def process_python_file(file_path: Path, overwrite_file: bool, stem_suffix: str):
    """
    Process a Python file by analyzing its AST, generating documentation,
    and writing the modified AST to a file.

    :param file_path: A Path object representing the path to the Python file to process.
    :type file_path: Path
    :param overwrite_file: A boolean indicating whether
     to overwrite the original file with the modified AST.
    :type overwrite_file: bool
    :param stem_suffix: A string to append to the stem of the original file name
     when creating the output file. If None, the original file name is used.
    :type stem_suffix: str"""
    print("Processing:", file_path)
    start_time = time.time()
    ast_analyzer = ASTAnalyzer()
    ast_analyzer.load_ast_from_file(file_path)
    file_visitor = FileVisitor(ast_analyzer)
    ast_analyzer.generate_documentation(file_visitor)
    output_file_path = file_path
    if overwrite_file is False and isinstance(stem_suffix, str):
        output_file_path = file_path.with_stem(file_path.stem + stem_suffix)
    ast_analyzer.write_file_from_ast(file_path=output_file_path)
    end_time = time.time()
    logging.info("Executed in %ds", end_time - start_time)


def process_directory(directory: Path, overwrite_file: bool, stem_suffix: str, disable_tqdm: bool):
    """
    Recursively process a directory by
     analyzing all Python files in the directory and its subdirectories.

    :param directory: A Path object representing the directory to process.
    :type directory: Path
    :param overwrite_file: A boolean indicating whether to overwrite the original file
     with the modified AST.
    :type overwrite_file: bool
    :param stem_suffix: A string to append to the stem of the original file name
     when creating the output file. If None, the original file name is used.
    :type stem_suffix: str
    :param disable_tqdm: A boolean indicating whether to disable the progress bar
     when processing the directory.
    :type disable_tqdm: bool"""
    dirs: list[Path]
    files: list[Path]
    for dirs, files in tqdm(path_walk(directory), disable=disable_tqdm):
        for current_dir in dirs:
            process_directory(current_dir, overwrite_file, stem_suffix, disable_tqdm)
        for current_file in files:
            if current_file.suffix == ".py" and current_file.name != "__init__.py":
                process_python_file(current_file, overwrite_file, stem_suffix)


def main():
    """
    The main function that processes Python files in a directory based on command-line arguments.

    The function parses command-line arguments using argparse and processes the specified file or
     directory using the process_python_file or process_directory functions, respectively.

    The function takes no arguments and returns nothing."""
    parser = argparse.ArgumentParser(description="Process Python files in a directory")
    parser.add_argument("path", help="path to Python file or directory")
    parser.add_argument(
        "-i",
        "--overwrite",
        "--inplace",
        action="store_true",
        help="Overwrite the file with the documentation injected",
    )
    parser.add_argument(
        "-s",
        "--suffix",
        help="The suffix to add to the stem of the Python files",
        type=str,
        default="_doc",
    )
    parser.add_argument("--disable_tqdm", help="Disable the progress bar", action="store_true")
    args = parser.parse_args()
    print(args)
    path: Path = Path(args.path)
    if path.is_file() and path.suffix == ".py":
        process_python_file(file_path=path, overwrite_file=args.overwrite, stem_suffix=args.suffix)
    elif path.is_dir():
        process_directory(
            directory=path,
            overwrite_file=args.overwrite,
            stem_suffix=args.suffix,
            disable_tqdm=args.disable_tqdm,
        )
    else:
        print("Invalid path or file type")


if __name__ == "__main__":
    main()
