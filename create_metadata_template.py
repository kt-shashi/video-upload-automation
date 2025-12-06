"""
Helper script to create metadata template files
Run this to generate video_metadata.csv or video_metadata.json templates
"""

from metadata_handler import create_metadata_template_csv, create_metadata_template_json
import sys

def main():
    print("=" * 60)
    print("Metadata Template Creator")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        format_type = sys.argv[1].lower()
    else:
        format_type = input("Choose format (csv/json) [default: csv]: ").strip().lower() or "csv"
    
    if format_type == "json":
        create_metadata_template_json()
    else:
        create_metadata_template_csv()
    
    print("\n" + "=" * 60)
    print("Template created successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit the metadata file to add information for your videos")
    print("2. Make sure the 'filename' column matches your video filenames exactly")
    print("3. Run your upload script - it will automatically use this metadata")
    print("\nExample:")
    print("  python create_metadata_template.py csv")
    print("  python create_metadata_template.py json")

if __name__ == '__main__':
    main()

