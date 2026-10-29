"""
Unit tests for Digital Notice Board System
Tests CRUD operations and sorting/filtering features.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database

class TestNoticeBoard(unittest.TestCase):
    def setUp(self):
        # Use an in-memory or dedicated test DB
        database.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_notice_board.db")
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)
        database.init_db()

    def tearDown(self):
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)

    def test_create_and_get_notice(self):
        notice = database.create_notice(
            title="Scholarship Applications Open",
            content="Merit scholarships are now accepting applications until end of month.",
            category="Academic",
            priority="High",
            author="Scholarship Bureau",
            is_pinned=1
        )
        self.assertIsNotNone(notice)
        self.assertEqual(notice["title"], "Scholarship Applications Open")
        self.assertEqual(notice["category"], "Academic")
        self.assertEqual(notice["is_pinned"], 1)

        fetched = database.get_notice_by_id(notice["id"])
        self.assertEqual(fetched["title"], "Scholarship Applications Open")

    def test_update_notice(self):
        notice = database.create_notice(
            title="Old Title",
            content="Old content",
            category="General"
        )
        updated = database.update_notice(
            notice["id"],
            title="Updated Title",
            priority="Urgent",
            content="New content"
        )
        self.assertEqual(updated["title"], "Updated Title")
        self.assertEqual(updated["priority"], "Urgent")
        self.assertEqual(updated["content"], "New content")

    def test_delete_notice(self):
        notice = database.create_notice(
            title="To Be Deleted",
            content="Temporary notice",
            category="General"
        )
        self.assertTrue(database.delete_notice(notice["id"]))
        self.assertIsNone(database.get_notice_by_id(notice["id"]))

    def test_sort_by_date(self):
        database.create_notice("Notice 1", "Content 1", "Category A", is_pinned=0)
        database.create_notice("Notice 2", "Content 2", "Category B", is_pinned=0)
        database.create_notice("Notice 3", "Content 3", "Category C", is_pinned=0)

        notices_desc = database.get_notices(sort_by="date_desc")
        self.assertEqual(len(notices_desc), 3)
        # Most recently created first
        self.assertEqual(notices_desc[0]["title"], "Notice 3")

        notices_asc = database.get_notices(sort_by="date_asc")
        self.assertEqual(notices_asc[0]["title"], "Notice 1")

    def test_sort_and_filter_by_category(self):
        database.create_notice("A Notice", "Content", "Events", is_pinned=0)
        database.create_notice("B Notice", "Content", "Academic", is_pinned=0)
        database.create_notice("C Notice", "Content", "Sports", is_pinned=0)

        # Filter by category
        events = database.get_notices(category="Events")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["title"], "A Notice")

        # Sort by category alphabetical
        sorted_cats = database.get_notices(sort_by="category_asc")
        cats = [n["category"] for n in sorted_cats]
        self.assertEqual(cats, ["Academic", "Events", "Sports"])

    def test_search_notices(self):
        database.create_notice("Fire Safety Drill", "Mandatory evacuation drill at 2 PM", "Safety")
        database.create_notice("Coding Hackathon", "36 hour programming sprint", "Events")

        results = database.get_notices(search="drill")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Fire Safety Drill")

if __name__ == "__main__":
    unittest.main()
