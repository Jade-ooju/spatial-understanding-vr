#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Mermaid diagrams from markdown and render them to PNG/SVG.
"""

import re
import os
import subprocess
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def extract_mermaid_diagrams(markdown_file):
    """Extract all Mermaid code blocks from markdown file."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all mermaid code blocks
    pattern = r'```mermaid\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    # Also find section headers before each diagram
    sections = []
    for match in re.finditer(pattern, content, re.DOTALL):
        # Find the section header before this match
        before_match = content[:match.start()]
        # Look for the last ## header
        headers = re.findall(r'^## (.+)$', before_match, re.MULTILINE)
        section_name = headers[-1] if headers else "diagram"
        sections.append((section_name, match.group(1)))
    
    return sections

def sanitize_filename(name):
    """Convert section name to valid filename."""
    # Remove special characters and convert to lowercase
    name = re.sub(r'[^\w\s-]', '', name.lower())
    name = re.sub(r'[-\s]+', '_', name)
    return name

def render_diagrams(markdown_file, output_dir='diagrams'):
    """Extract and render all Mermaid diagrams."""
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Extract diagrams
    diagrams = extract_mermaid_diagrams(markdown_file)
    
    print(f"Found {len(diagrams)} diagrams to render...")
    
    rendered_files = []
    
    for i, (section_name, diagram_code) in enumerate(diagrams, 1):
        filename_base = sanitize_filename(section_name)
        mmd_file = output_path / f"{filename_base}.mmd"
        png_file = output_path / f"{filename_base}.png"
        svg_file = output_path / f"{filename_base}.svg"
        
        # Write Mermaid file
        with open(mmd_file, 'w', encoding='utf-8') as f:
            f.write(diagram_code)
        
        print(f"\n[{i}/{len(diagrams)}] Rendering: {section_name}")
        print(f"  MMD file: {mmd_file}")
        
        # Render to PNG with high quality
        try:
            # Use npx on Windows, or try mmdc directly
            import shutil
            mmdc_cmd = shutil.which('mmdc') or 'npx'
            if mmdc_cmd == 'npx':
                cmd_png = ['npx', '-y', '@mermaid-js/mermaid-cli', '-i', str(mmd_file), '-o', str(png_file), 
                          '-t', 'default', '-b', 'white', '-w', '2400', '-H', '1800', '-s', '2']
            else:
                cmd_png = [mmdc_cmd, '-i', str(mmd_file), '-o', str(png_file), 
                          '-t', 'default', '-b', 'white', '-w', '2400', '-H', '1800', '-s', '2']
            result = subprocess.run(cmd_png, capture_output=True, text=True, check=True, shell=True)
            print(f"  [OK] PNG (HQ): {png_file}")
            rendered_files.append(('PNG', png_file))
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] PNG failed: {e.stderr}")
        except Exception as e:
            print(f"  [ERROR] PNG failed: {e}")
        
        # Render to SVG (vector, always high quality)
        try:
            import shutil
            mmdc_cmd = shutil.which('mmdc') or 'npx'
            if mmdc_cmd == 'npx':
                cmd_svg = ['npx', '-y', '@mermaid-js/mermaid-cli', '-i', str(mmd_file), '-o', str(svg_file), '-t', 'default']
            else:
                cmd_svg = [mmdc_cmd, '-i', str(mmd_file), '-o', str(svg_file), '-t', 'default']
            result = subprocess.run(cmd_svg, capture_output=True, text=True, check=True, shell=True)
            print(f"  [OK] SVG: {svg_file}")
            rendered_files.append(('SVG', svg_file))
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] SVG failed: {e.stderr}")
        except Exception as e:
            print(f"  [ERROR] SVG failed: {e}")
    
    print(f"\n{'='*70}")
    print(f"Rendering complete!")
    print(f"Output directory: {output_path.absolute()}")
    print(f"Total files rendered: {len(rendered_files)}")
    print(f"{'='*70}")
    
    return rendered_files

if __name__ == '__main__':
    # Find the markdown file in docs/ directory (one level up from scripts/)
    project_root = Path(__file__).parent.parent
    markdown_file = project_root / 'docs' / 'VIDEO_PIPELINE_UML_DIAGRAMS.md'
    if not markdown_file.exists():
        print(f"Error: {markdown_file} not found")
        exit(1)
    
    # Output diagrams to diagrams/ directory
    output_dir = project_root / 'diagrams'
    render_diagrams(markdown_file, output_dir=output_dir)
