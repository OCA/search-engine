# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from ..models.backend import SearchEngineBackend
    from ..models.index import SearchEngineIndex


class SearchEngineAdapter(ABC):
    def __init__(
        self, backend_record: SearchEngineBackend, index_record: SearchEngineIndex
    ):
        super().__init__()
        self.backend_record = backend_record
        self.index_record = index_record

    @abstractmethod
    def index(self, datas: list[dict[str, Any]]) -> None:
        """Index the data into the index on the search engine."""
        ...

    @abstractmethod
    def delete(self, binding_ids: list[int]) -> None:
        """Delete the data from the index on the search engine.

        The binding_ids are the ids of the record in the index.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear the index content on the search engine."""
        ...

    @abstractmethod
    def each(self, fetch_fields: list[str] | None = None) -> Iterator[dict[str, Any]]:
        """Return an iterator on the index content."""
        ...

    def reindex(self) -> None:
        """Reindex the index on the search engine side."""
        self.clear()
        self.index(self._get_index_data())

    def settings(self, force=False) -> None:
        """Update the settings of the index on the search engine side."""

    def test_connection(self) -> None:
        """Test the connection to the search engine.

        It should raise an exception if the connection is not working.
        """
