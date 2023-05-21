from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass
class Cycler(Iterator[T]):
    """
    Iterable that iterates over the provided deque over forever, but with a
    method to select specific items in the deque to consume on demand.
    """

    elements: deque[T]

    def consume(self, element: T) -> T:
        """
        Find the first instance of the given element in the deque, then move it
        to the end of the deque. Return the element.

        If the element is not in the queue, do nothing.

        """
        try:
            self.elements.remove(element)
        except ValueError as e:
            raise ValueError(f"not found: {element}") from e
        else:
            self.elements.append(element)
        return element

    def __next__(self) -> T:
        """
        Return the next element in the deque, and place it back on the end of
        the deque.
        """
        element = self.elements.popleft()
        self.elements.append(element)
        return element
