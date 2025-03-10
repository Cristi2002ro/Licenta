
documentation_prompt = """""
    Generate documentation based on the provided context code. Include a descriptive title, a concise introduction, sections for features, installation, usage (with relevant code examples), and a conclusion. The output must be in Markdown format.
"""

unit_tests_prompt = """
Generate unit tests for the provided context code. Cover typical cases, edge cases, and potential error conditions using the appropriate testing framework. Return only the test code without any extra explanations or formatting"""

code_review = """
Perform a detailed review of the provided context code. Identify any errors, performance issues, refactoring opportunities, and suggest improvements for clarity and design. Format your review in Markdown
"""