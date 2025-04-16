# Mind Map Application

A Python-based mind mapping application built with Tkinter that allows you to create, edit, and organize ideas visually.

## Features

- Create nodes with resizable boxes
- Edit text directly within nodes
- Drag and drop nodes to organize
- Connect nodes with arrows
- Customize node colors
- Resize nodes using handles
- Clear and intuitive interface

## Requirements

- Python 3.x
- Tkinter (usually comes with Python)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/acon6/mindmap-tk.git
cd mindmap-tk
```

2. Run the application:
```bash
python mindmap_tk.py
```

## Usage

1. **Creating Nodes**:
   - Click the "Add Node" button in the toolbar
   - Right-click anywhere on the canvas and select "Add Node"

2. **Editing Text**:
   - Double-click any node to edit its text
   - Type your text directly in the box
   - Click outside or press Tab to finish editing

3. **Moving Nodes**:
   - Click and drag anywhere on a node (except the resize handle)
   - The node will move smoothly with your cursor

4. **Resizing Nodes**:
   - Click and drag the small gray handle in the bottom-right corner
   - The node will resize, and text will adjust automatically

5. **Connecting Nodes**:
   - Select a source node (it will show a blue outline)
   - Click the "Connect Nodes" button
   - Click a target node to create an arrow connection

6. **Customizing Colors**:
   - Right-click a node and select "Change Color"
   - Choose a color from the color picker
   - Both the box and text area will update to the new color

7. **Clearing the Mind Map**:
   - Click the "Clear All" button to remove everything
   - Confirm the action in the popup dialog

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.