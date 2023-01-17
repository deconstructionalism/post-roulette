from tinydb import TinyDB, Query
from tinydb.table import Document
from typing import List, Optional


class Posts:
    """
    Post controls a named table ("posts") with documents that
    correspond to post within the source data.
    """

    def __init__(self, db: TinyDB) -> None:
        self.db = db
        self.table = db.table("posts")

    @staticmethod
    def _unique_query(source_name: str, index: int) -> Query:
        """Generate a TinyDB query for a unique post."""

        Post = Query()
        return (Post.source_name == source_name) & (Post.index == index)

    def get(self, source_name: str, index: int) -> Optional[Document]:
        """Get a post for a source by `index` if it exists."""

        return self.table.get(Posts._unique_query(source_name, index))

    def get_all(self, source_name: str) -> List[Document]:
        """Get all posts for a source."""

        return self.table.search(Query().source_name == source_name)

    def create(self, source_name: str, index: int, content: str, datetime: str) -> int:
        """
        Create a post for a source and return the number of posts created.

        This will overwrite another post with the same `index` if it exists.
        """

        inserted = self.table.upsert(
            dict(
                source_name=source_name, index=index, content=content, datetime=datetime
            ),
            Posts._unique_query(source_name, index),
        )

        return len(inserted)

    def delete(self, source_name: str, index: int) -> int:
        """
        Delete a post by `index` for a given source if it exists and return
        the number of posts deleted.
        """

        deleted = self.table.remove(Posts._unique_query(source_name, index))

        return len(deleted)
