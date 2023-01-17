from typing import Optional, TypeVar

from tinydb import Query, TinyDB
from tinydb.table import Document

# HELPER FUNCTIONS

T = TypeVar("T")


def unwrap(val: Optional[T]) -> T:
    assert val is not None

    return val


class Cursors:
    """
    Cursors controls a named table ("cursors") that keeps track of the
    last post index that the user took action on for that source.
    """

    def __init__(self, db: TinyDB) -> None:
        self.db = db
        self.table = db.table("cursor")

    def get_value(self, source_name: str) -> int:
        """
        Get the value of the cursor for a given source.

        If cursor does not exist for source, create one.
        """

        def get_doc() -> Optional[Document]:
            return self.table.get(Query().source_name == source_name)

        document = get_doc()

        if not document:
            self.set_value(source_name, 0)
            document = unwrap(get_doc())

        value = int(unwrap(document.get("value")))

        return value

    def set_value(self, source_name: str, value: int) -> int:
        """
        Set the value of the cursor for a given source and return the number
        of cursors updated.
        """

        updated = self.table.upsert(
            dict(source_name=source_name, value=value),
            Query().source_name == source_name,
        )

        return len(updated)
