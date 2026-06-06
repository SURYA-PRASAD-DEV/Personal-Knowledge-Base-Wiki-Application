"""
Seed script to create sample articles for the PKB demo.

Usage:
  python seed.py

Make sure `serviceAccountKey.json` is in project root or configure FIREBASE_CREDENTIALS.
"""
from models import create_article, add_version

def main():
    a1 = create_article('Welcome', 'This is your personal knowledge base. Link to [[Getting Started]].', ['intro','general'])
    a2 = create_article('Getting Started', 'Steps:\n1. Create an article\n2. Use [[Welcome]] to navigate', ['guide'])
    add_version(a1['id'], 'Initial version of Welcome', edited_by='System')
    print('Seeded sample articles: Welcome, Getting Started')

if __name__ == '__main__':
    main()
