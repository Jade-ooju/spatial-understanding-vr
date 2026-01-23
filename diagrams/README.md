# Rendered UML Diagrams

This directory contains rendered images of all UML diagrams from `VIDEO_PIPELINE_UML_DIAGRAMS.md`.

## Generated Files

All diagrams are available in both **PNG** (raster) and **SVG** (vector) formats.

### 1. Component Diagram
- `component_diagram.png` / `component_diagram.svg`
- Shows high-level architecture and relationships between major components

### 2. Sequence Diagram
- `sequence_diagram.png` / `sequence_diagram.svg`
- Shows interaction flow between components during video processing

### 3. Activity Diagram
- `activity_diagram.png` / `activity_diagram.svg`
- Shows detailed workflow and decision points in the processing pipeline

### 4. Class Diagram
- `class_diagram.png` / `class_diagram.svg`
- Shows class structure and relationships (mostly functional design with PhysicsEstimator)

### 5. Data Flow Diagram
- `data_flow_diagram.png` / `data_flow_diagram.svg`
- Shows how data flows through the system from input to output

### 6. State Diagram
- `state_diagram.png` / `state_diagram.svg`
- Shows state transitions during video processing

### 7. Package Diagram
- `package_diagram.png` / `package_diagram.svg`
- Shows module organization and dependencies

### 8. Interaction Overview Diagram
- `interaction_overview_diagram.png` / `interaction_overview_diagram.svg`
- Shows high-level interaction summary

## Usage

- **PNG files**: Best for presentations, documentation, and quick viewing
- **SVG files**: Best for scaling, editing, and high-quality printing

## Regenerating Diagrams

To regenerate these diagrams, run:

```bash
python render_diagrams.py
```

This will extract all Mermaid diagrams from `VIDEO_PIPELINE_UML_DIAGRAMS.md` and render them to this directory.

## Requirements

- Node.js and npm
- @mermaid-js/mermaid-cli (installed globally or via npx)
- Python 3 (for the extraction script)
