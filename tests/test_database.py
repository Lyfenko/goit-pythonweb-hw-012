import unittest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from database import engine


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.Session = sessionmaker(bind=engine)

    def test_database_connection(self):
        session = self.Session()

        try:
            result = session.execute(text("SELECT 1"))
            self.assertEqual(result.scalar(), 1)
        finally:
            session.close()


if __name__ == '__main__':
    unittest.main()
