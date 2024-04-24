import os

def adjust_header_level(text, levels_to_increase):
    """Adjust the markdown header levels in the text, converting deep levels to bold text."""
    lines = text.split('\n')
    adjusted_lines = []
    for line in lines:
        if line.startswith('#'):
            # Count the number of '#' to determine the current level
            current_level = len(line.split(' ')[0])
            # Calculate new level
            new_level = current_level + levels_to_increase
            if new_level <= 4:
                # Adjust the line with the new level
                adjusted_line = '#' * new_level + ' ' + ' '.join(line.split(' ')[1:])
            else:
                # Convert to bold text for levels deeper than 4
                adjusted_line = '**' + ' '.join(line.split(' ')[1:]) + '**'
            adjusted_lines.append(adjusted_line)
        else:
            adjusted_lines.append(line)
    return '\n'.join(adjusted_lines)

def merge_markdown_files(root_dir, output_file):
    """Merge all markdown files in the directory structure into a single file."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(root_dir):
            relative_path = os.path.relpath(root, root_dir)
            if relative_path != ".":
                # Split the relative path to get the depth and names for headers
                parts = relative_path.split(os.sep)
                for i, part in enumerate(parts):
                    outfile.write('#' * (i + 1) + ' ' + part + '\n')
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    header_level = len(relative_path.split(os.sep))
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        adjusted_content = adjust_header_level(content, header_level)
                        outfile.write(adjusted_content + '\n\n')

# Example usage
merge_markdown_files('docs', 'merged_markdown.md')
