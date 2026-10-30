def format_patch_instruction() -> str:
    return (
        "Format your code edits using strict SEARCH/REPLACE blocks.\n"
        "Rules:\n"
        "- The SEARCH section must match exact lines from the existing file.\n"
        "- The REPLACE section contains the updated lines.\n"
        "- Ensure the patched file remains syntactically valid Python.\n"
        "- Do not edit files under tests/.\n"
    )
