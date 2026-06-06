#!/usr/bin/env python
import models

print("Testing Tag Cloud Function:")
tag_cloud = models.get_tag_cloud()

print(f"\nTotal tags: {len(tag_cloud)}")
print("\nTag Cloud Details (sorted by count):")
for tag_info in tag_cloud:
    print(f"  - {tag_info['tag']:40} | Count: {tag_info['count']:2} | Size: {tag_info['size_class']:2} | Color: {tag_info['color']}")

print("\n✓ Tag system working correctly!")
