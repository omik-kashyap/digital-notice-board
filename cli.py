#!/usr/bin/env python3
"""
Interactive Command-Line Interface (CLI) for Digital Notice Board System.
Administrators can post, update, delete, search, and view notices sorted by date or category.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_date(dt_str):
    if not dt_str:
        return "-"
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%b %d, %Y %I:%M %p")
    except Exception:
        return str(dt_str)

def print_header(title):
    print("\n" + "=" * 65)
    print(f" 📢  {title.upper()}")
    print("=" * 65)

def display_notice_card(notice, show_full_content=False):
    pin_badge = "📌 [PINNED]" if notice.get('is_pinned') else ""
    priority = notice.get('priority', 'Normal')
    priority_color = {
        'Urgent': '🚨 URGENT',
        'High': '⚡ HIGH',
        'Normal': '🔹 NORMAL',
        'Low': '◽ LOW'
    }.get(priority, priority)
    
    print("-" * 65)
    print(f"ID: #{notice['id']} | Category: [{notice['category']}] | Priority: {priority_color} {pin_badge}")
    print(f"Title: {notice['title']}")
    print(f"Author: {notice['author']} | Date: {format_date(notice['created_at'])}")
    if notice.get('expires_at'):
        print(f"Expires On: {notice['expires_at']}")
    print("-" * 65)
    
    content = notice['content']
    if not show_full_content and len(content) > 140:
        print(f"Notice: {content[:137]}... (view full notice for details)")
    else:
        print(f"Notice:\n{content}")
    print("-" * 65 + "\n")

def view_notices_menu():
    while True:
        print("\n--- VIEW NOTICES SORTED & FILTERED ---")
        print("1. Sort by Date (Newest First)")
        print("2. Sort by Date (Oldest First)")
        print("3. Sort by Category (Alphabetical)")
        print("4. Sort by Priority (Urgent First)")
        print("5. Filter by Specific Category")
        print("6. Search Notices by Keyword")
        print("0. Back to Main Menu")
        
        choice = input("Enter option [0-6]: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            notices = database.get_notices(sort_by="date_desc")
            show_notices_list(notices, "Notices Sorted by Date (Newest First)")
        elif choice == "2":
            notices = database.get_notices(sort_by="date_asc")
            show_notices_list(notices, "Notices Sorted by Date (Oldest First)")
        elif choice == "3":
            notices = database.get_notices(sort_by="category_asc")
            show_notices_list(notices, "Notices Sorted by Category")
        elif choice == "4":
            notices = database.get_notices(sort_by="priority")
            show_notices_list(notices, "Notices Sorted by Priority")
        elif choice == "5":
            categories = database.get_categories()
            if not categories:
                print("No categories found.")
                continue
            print("\nAvailable Categories:")
            for idx, cat in enumerate(categories, 1):
                print(f"  {idx}. {cat}")
            cat_choice = input("Enter category name or number: ").strip()
            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                selected_cat = categories[int(cat_choice) - 1]
            else:
                selected_cat = cat_choice
            notices = database.get_notices(category=selected_cat)
            show_notices_list(notices, f"Notices in Category: '{selected_cat}'")
        elif choice == "6":
            keyword = input("Enter search keyword (title, content, author, category): ").strip()
            if keyword:
                notices = database.get_notices(search=keyword)
                show_notices_list(notices, f"Search Results for '{keyword}'")
        else:
            print("Invalid choice, please select 0 to 6.")

def show_notices_list(notices, title):
    print_header(f"{title} (Found: {len(notices)})")
    if not notices:
        print("No notices found matching criteria.")
        return
        
    for n in notices:
        display_notice_card(n, show_full_content=False)
        
    sub_action = input("Enter a Notice ID to view full details (or press Enter to return): ").strip()
    if sub_action.isdigit():
        notice = database.get_notice_by_id(int(sub_action))
        if notice:
            print("\n" + "=" * 65)
            print("FULL NOTICE DETAILS")
            display_notice_card(notice, show_full_content=True)
            input("Press Enter to continue...")
        else:
            print(f"Notice with ID #{sub_action} not found.")

def post_notice_cli():
    print_header("POST NEW NOTICE (ADMIN)")
    title = input("Enter Notice Title: ").strip()
    if not title:
        print("Error: Title cannot be empty!")
        return
        
    print("\nExisting categories:", ", ".join(database.get_categories()) or "None")
    category = input("Enter Category (e.g., Academic, Urgent, Events, General, Technical): ").strip()
    if not category:
        category = "General"
        
    print("\nPriority options: 1. Urgent  2. High  3. Normal  4. Low")
    p_choice = input("Choose priority [1-4, default Normal]: ").strip()
    priority_map = {"1": "Urgent", "2": "High", "3": "Normal", "4": "Low"}
    priority = priority_map.get(p_choice, "Normal")
    
    author = input("Enter Author / Department [Default: Admin Office]: ").strip()
    if not author:
        author = "Admin Office"
        
    pin_choice = input("Pin this notice to top? (y/N): ").strip().lower()
    is_pinned = 1 if pin_choice in ('y', 'yes') else 0
    
    expires_at = input("Expiration date (YYYY-MM-DD or leave blank): ").strip()
    
    print("\nEnter Notice Content / Announcement (Type or paste body text):")
    content = input("> ").strip()
    if not content:
        print("Error: Notice content cannot be empty!")
        return
        
    created = database.create_notice(
        title=title,
        content=content,
        category=category,
        priority=priority,
        author=author,
        is_pinned=is_pinned,
        expires_at=expires_at or None
    )
    
    print("\n✅ Notice posted successfully!")
    display_notice_card(created, show_full_content=True)

def update_notice_cli():
    print_header("UPDATE EXISTING NOTICE (ADMIN)")
    notice_id = input("Enter Notice ID to update: ").strip()
    if not notice_id.isdigit():
        print("Invalid ID.")
        return
        
    notice = database.get_notice_by_id(int(notice_id))
    if not notice:
        print(f"Notice #{notice_id} not found!")
        return
        
    print("\nCurrent Notice:")
    display_notice_card(notice, show_full_content=True)
    print("Leave fields blank to keep existing values.\n")
    
    title = input(f"New Title [{notice['title']}]: ").strip()
    category = input(f"New Category [{notice['category']}]: ").strip()
    
    print(f"Current Priority: {notice['priority']} (1. Urgent  2. High  3. Normal  4. Low)")
    p_choice = input("New Priority [1-4 or leave blank]: ").strip()
    priority_map = {"1": "Urgent", "2": "High", "3": "Normal", "4": "Low"}
    priority = priority_map.get(p_choice, None)
    
    author = input(f"New Author [{notice['author']}]: ").strip()
    
    curr_pin_str = "Yes" if notice['is_pinned'] else "No"
    pin_choice = input(f"Pinned to Top? Current: {curr_pin_str} (y/n or blank to keep): ").strip().lower()
    is_pinned = None
    if pin_choice in ('y', 'yes'):
        is_pinned = 1
    elif pin_choice in ('n', 'no'):
        is_pinned = 0
        
    expires_at = input(f"New Expiry Date [{notice.get('expires_at') or 'None'}]: ").strip()
    
    print(f"\nCurrent Content:\n{notice['content']}")
    content = input("New Content (or leave blank to keep): ").strip()
    
    updated = database.update_notice(
        notice_id=int(notice_id),
        title=title or None,
        content=content or None,
        category=category or None,
        priority=priority or None,
        author=author or None,
        is_pinned=is_pinned,
        expires_at=expires_at or None
    )
    
    print("\n✅ Notice updated successfully!")
    display_notice_card(updated, show_full_content=True)

def delete_notice_cli():
    print_header("DELETE NOTICE (ADMIN)")
    notice_id = input("Enter Notice ID to delete: ").strip()
    if not notice_id.isdigit():
        print("Invalid ID.")
        return
        
    notice = database.get_notice_by_id(int(notice_id))
    if not notice:
        print(f"Notice #{notice_id} not found!")
        return
        
    display_notice_card(notice, show_full_content=False)
    confirm = input(f"⚠️ Are you sure you want to permanently delete Notice #{notice_id}? (y/N): ").strip().lower()
    
    if confirm in ('y', 'yes'):
        success = database.delete_notice(int(notice_id))
        if success:
            print(f"✅ Notice #{notice_id} has been deleted.")
        else:
            print("Failed to delete notice.")
    else:
        print("Deletion cancelled.")

def main_menu():
    database.init_db()
    database.seed_sample_notices()
    
    while True:
        stats = database.get_stats()
        print("\n" + "=" * 65)
        print(" 🏛️  DIGITAL NOTICE BOARD SYSTEM - ADMIN & VIEWER CONSOLE")
        print("=" * 65)
        print(f" 📊 Stats: Total Notices: {stats['total']} | Urgent: {stats['urgent']} | Pinned: {stats['pinned']} | Categories: {stats['categories_count']}")
        print("=" * 65)
        print(" 1. 📋 View Notices (Sort by Date, Category, Priority, Filter)")
        print(" 2. ➕ Post New Notice (Admin)")
        print(" 3. ✏️  Update Existing Notice (Admin)")
        print(" 4. 🗑️  Delete Notice (Admin)")
        print(" 5. 🔍 Quick Search Notices")
        print(" 6. ℹ️  System Info & Categories List")
        print(" 0. 🚪 Exit")
        print("=" * 65)
        
        choice = input("Select an option [0-6]: ").strip()
        
        if choice == "1":
            view_notices_menu()
        elif choice == "2":
            post_notice_cli()
        elif choice == "3":
            update_notice_cli()
        elif choice == "4":
            delete_notice_cli()
        elif choice == "5":
            keyword = input("\nEnter search keyword: ").strip()
            if keyword:
                notices = database.get_notices(search=keyword)
                show_notices_list(notices, f"Search Results for '{keyword}'")
        elif choice == "6":
            cats = database.get_categories()
            print("\nAvailable Categories:", ", ".join(cats) or "None")
            print(f"Database file: {database.DB_PATH}")
        elif choice == "0":
            print("\nThank you for using Digital Notice Board System. Goodbye!\n")
            sys.exit(0)
        else:
            print("Invalid option. Please choose between 0 and 6.")

if __name__ == "__main__":
    main_menu()
