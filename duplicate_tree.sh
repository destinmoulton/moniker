#!/bin/bash

# Script to duplicate directory structure with smaller placeholder files
# Usage: ./duplicate_tree.sh <source_dir> <destination_dir> [file_size_kb]

if [ $# -lt 2 ]; then
    echo "Usage: $0 <source_dir> <destination_dir> [file_size_kb]"
    echo "  source_dir: Directory to duplicate"
    echo "  destination_dir: Where to create the duplicate"
    echo "  file_size_kb: Size of placeholder files in KB (default: 1)"
    exit 1
fi

SOURCE_DIR="$1"
DEST_DIR="$2"
FILE_SIZE_KB="${3:-1}"  # Default to 1KB if not specified

# Validate source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist"
    exit 1
fi

# Create destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
    mkdir -p "$DEST_DIR"
    echo "Created destination directory: $DEST_DIR"
fi

echo "Duplicating directory structure from '$SOURCE_DIR' to '$DEST_DIR'"
echo "Placeholder file size: ${FILE_SIZE_KB}KB"
echo ""

# Counter for statistics
dir_count=0
file_count=0

# Use find to traverse the source directory
while IFS= read -r -d '' source_path; do
    # Get relative path from source directory
    relative_path="${source_path#$SOURCE_DIR/}"
    dest_path="$DEST_DIR/$relative_path"
    
    if [ -d "$source_path" ]; then
        # Create directory
        mkdir -p "$dest_path"
        ((dir_count++))
    elif [ -f "$source_path" ]; then
        # Get the extension
        extension="${source_path##*.}"
        
        # Create parent directory if needed
        dest_parent=$(dirname "$dest_path")
        mkdir -p "$dest_parent"
        
        # Create small placeholder file with same extension
        # Use dd to create a file of specific size
        dd if=/dev/zero of="$dest_path" bs=1024 count=$FILE_SIZE_KB 2>/dev/null
        
        ((file_count++))
        
        # Show progress every 100 files
        if [ $((file_count % 100)) -eq 0 ]; then
            echo "Progress: $file_count files created..."
        fi
    fi
done < <(find "$SOURCE_DIR" -print0)

echo ""
echo "Duplication complete!"
echo "Directories created: $dir_count"
echo "Files created: $file_count"
echo "Destination: $DEST_DIR"
