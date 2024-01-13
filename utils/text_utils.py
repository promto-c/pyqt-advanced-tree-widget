import re
from typing import List


class TextExtraction:
    """Provides static methods for extracting quoted and unquoted terms from strings.
    """
    @staticmethod
    def extract_quoted_terms(keyword: str) -> List[str]:
        """Extracts terms enclosed in quotes from the given keyword string.

        Terms enclosed in either double or single quotes are considered quoted terms.

        Args:
            keyword: The keyword string containing the terms.

        Returns:
            A list of quoted terms.

        Example:
            >>> TextExtraction.extract_quoted_terms("'apple' \\" banana\\" grape \\"orange and mango\\"")
            ['apple', 'banana', 'orange and mango']
        """
        quoted_terms = re.findall(r'"(.*?)"|\'(.*?)\'', keyword)
        return [term.strip() for terms in quoted_terms for term in terms if term.strip()]

    @staticmethod
    def extract_unquoted_terms(keyword: str) -> List[str]:
        """Extracts terms not enclosed in quotes from the given keyword string.

        Terms not enclosed in quotes are considered unquoted terms, split on tabs,
        new lines, commas, or pipes.

        Args:
            keyword: The keyword string containing the terms.

        Returns:
            A list of unquoted terms.

        Example:
            >>> TextExtraction.extract_unquoted_terms("'apple' \\" banana\\" grape \\"orange and mango\\"")
            ['grape']
        """
        unquoted_terms = [term.strip() for term in re.split(r'"[^"]*"|\'[^\']*\'', keyword) if term.strip()]
        return [split_term for term in unquoted_terms for split_term in re.split('[\t\n,|]+', term) if split_term.strip()]

    @staticmethod
    def split_keywords(text: str) -> List[str]:
        """Splits the given text into keywords based on common delimiters.

        Args:
            text: A string to be split.

        Returns:
            A list of split keywords.

        Examples:
            >>> TextExtraction.split_keywords('apple, banana|grape\\torange\\nmango')
            ['apple', ' banana', 'grape', 'orange', 'mango']
        """
        return re.split('[\t\n,|]+', text)

    @staticmethod
    def is_contains_wildcard(text: str) -> bool:
        """Checks if the given text contains any wildcard characters ('*' or '?').

        Args:
            text: A string in which to check for wildcards.

        Returns:
            True if wildcards are present, False otherwise.

        Examples:
            >>> TextExtraction.is_contains_wildcard('apple*')
            True
            >>> TextExtraction.is_contains_wildcard('banana')
            False
        """
        return '*' in text or '?' in text

if __name__ == "__main__":
    import doctest
    doctest.testmod()
