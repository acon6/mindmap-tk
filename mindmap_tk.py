"""
Simple mind map application using Tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import json
from typing import Dict, List, Optional
import math

class Node:
    def __init__(self, title: str, x: int, y: int):
        self.title = title
        self.x = x
        self.y = y
        self.width = 100  # Initial width
        self.height = 60  # Initial height
        self.connections: List['Node'] = []
        self.text_widget = None  # Reference to the text widget
        self.color = 'white'  # Default color

class MindMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mind Map")
        
        # Configure main window
        self.root.geometry("800x600")
        
        # Create canvas
        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Node storage
        self.nodes: Dict[int, Node] = {}
        self.next_node_id = 1
        
        # Interaction state
        self.selected_node = None
        self.connecting_source = None
        self.resize_mode = False
        self.resize_start = None
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Button-3>', self.on_right_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<Double-Button-1>', self.on_double_click)
        
        # Create toolbar
        self.create_toolbar()
        
    def create_toolbar(self):
        """Create the application toolbar"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Add node button
        add_btn = ttk.Button(toolbar, text="Add Node", command=self.add_node)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Connect nodes button
        connect_btn = ttk.Button(toolbar, text="Connect Nodes", command=self.start_connecting)
        connect_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = ttk.Button(toolbar, text="Clear All", command=self.clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def add_node(self, x: Optional[int] = None, y: Optional[int] = None):
        """Add a new node to the mind map"""
        if x is None or y is None:
            # If no position specified, use center of canvas
            x = self.canvas.winfo_width() // 2
            y = self.canvas.winfo_height() // 2
        
        # Create node
        node = Node(f"Node {self.next_node_id}", x, y)
        node_id = self.next_node_id
        self.nodes[node_id] = node
        self.next_node_id += 1
        
        # Draw node
        self.draw_node(node_id)
        
    def draw_node(self, node_id: int):
        """Draw a node on the canvas"""
        node = self.nodes[node_id]
        
        # Calculate box coordinates
        x1 = node.x - node.width//2
        y1 = node.y - node.height//2
        x2 = node.x + node.width//2
        y2 = node.y + node.height//2
        
        # Draw node box
        box_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=node.color, outline='black', tags=(f'node{node_id}', f'box{node_id}'))
        
        # Create text widget for editing
        text_widget = tk.Text(self.canvas, wrap=tk.WORD, borderwidth=0, highlightthickness=0)
        text_widget.insert('1.0', node.title)
        text_widget.bind('<FocusOut>', lambda e, nid=node_id: self.on_text_changed(nid))
        text_widget.bind('<Tab>', lambda e: self.canvas.focus_set())
        
        # Calculate text widget size based on box size
        padding = 4  # Pixels of padding inside the box
        text_width = node.width - (2 * padding)  # Pixels
        text_height = node.height - (2 * padding)  # Pixels
        
        # Convert pixel sizes to character units (approximate)
        char_width = max(1, text_width // 8)  # Assuming average char width of 8 pixels
        char_height = max(1, text_height // 20)  # Assuming average char height of 20 pixels
        
        text_widget.configure(
            width=char_width,
            height=char_height,
            bg=node.color,
            padx=padding,
            pady=padding
        )
        
        # Add text widget to canvas, centered in the box
        text_window = self.canvas.create_window(
            node.x, node.y,
            window=text_widget,
            width=node.width - 2,  # Slight adjustment to prevent overflow
            height=node.height - 2,
            tags=(f'node{node_id}', f'text{node_id}')
        )
        
        # Store reference to text widget
        node.text_widget = text_widget
        
        # Create resize handle
        handle_size = 6
        handle_id = self.canvas.create_rectangle(
            x2 - handle_size, y2 - handle_size,
            x2, y2,
            fill='gray', tags=(f'node{node_id}', f'handle{node_id}')
        )
        
        # Bind events
        self.canvas.tag_bind(f'node{node_id}', '<Button-1>', lambda e: self.select_node(node_id))
        self.canvas.tag_bind(f'handle{node_id}', '<Button-1>', lambda e: self.start_resize(node_id, e))
        self.canvas.tag_bind(f'handle{node_id}', '<B1-Motion>', lambda e: self.on_resize(node_id, e))
        self.canvas.tag_bind(f'box{node_id}', '<B1-Motion>', lambda e: self.on_drag(e))
    
    def start_resize(self, node_id: int, event):
        """Start resizing a node"""
        self.resize_mode = True
        self.resize_start = (event.x, event.y)
        self.select_node(node_id)
    
    def on_resize(self, node_id: int, event):
        """Handle node resizing"""
        if self.resize_mode and self.resize_start:
            node = self.nodes[node_id]
            
            # Calculate new dimensions
            dx = event.x - self.resize_start[0]
            dy = event.y - self.resize_start[1]
            
            # Update node dimensions (with minimum size)
            node.width = max(100, node.width + dx)
            node.height = max(60, node.height + dy)
            
            # Update node graphics
            self.redraw_node(node_id)
            self.update_connections()
            
            # Update resize start point
            self.resize_start = (event.x, event.y)
    
    def redraw_node(self, node_id: int):
        """Redraw a node with updated dimensions"""
        node = self.nodes[node_id]
        
        # Update box
        x1 = node.x - node.width//2
        y1 = node.y - node.height//2
        x2 = node.x + node.width//2
        y2 = node.y + node.height//2
        
        # Update box coordinates
        box_items = self.canvas.find_withtag(f'box{node_id}')
        if box_items:
            self.canvas.coords(box_items[0], x1, y1, x2, y2)
        
        # Update text widget
        if node.text_widget:
            # Update text widget size and position
            padding = 4
            text_width = node.width - (2 * padding)
            text_height = node.height - (2 * padding)
            char_width = max(1, text_width // 8)
            char_height = max(1, text_height // 20)
            
            node.text_widget.configure(
                width=char_width,
                height=char_height,
                bg=node.color
            )
            
            # Update text widget position
            text_items = self.canvas.find_withtag(f'text{node_id}')
            if text_items:
                self.canvas.coords(text_items[0], node.x, node.y)
                self.canvas.itemconfig(text_items[0],
                    width=node.width - 2,
                    height=node.height - 2
                )
        
        # Update resize handle
        handle_size = 6
        handle_items = self.canvas.find_withtag(f'handle{node_id}')
        if handle_items:
            self.canvas.coords(handle_items[0],
                x2 - handle_size, y2 - handle_size,
                x2, y2
            )
    
    def draw_connection(self, source: Node, target: Node):
        """Draw a connection between two nodes"""
        # Calculate connection points from the edges of the boxes
        # Get source point
        angle = math.atan2(target.y - source.y, target.x - source.x)
        source_x = source.x + math.cos(angle) * source.width/2
        source_y = source.y + math.sin(angle) * source.height/2
        
        # Get target point
        angle = math.atan2(source.y - target.y, source.x - target.x)
        target_x = target.x + math.cos(angle) * target.width/2
        target_y = target.y + math.sin(angle) * target.height/2
        
        # Draw line with arrow
        line_id = self.canvas.create_line(
            source_x, source_y, target_x, target_y,
            arrow=tk.LAST, fill='gray'
        )
        
        # Move line to background
        self.canvas.tag_lower(line_id)
    
    def select_node(self, node_id: int):
        """Select a node"""
        # Deselect previous node
        if self.selected_node is not None:
            self.canvas.itemconfig(f'box{self.selected_node}', outline='black')
        
        # Select new node
        self.selected_node = node_id
        self.canvas.itemconfig(f'box{node_id}', outline='blue', width=2)
        
        # If connecting nodes
        if self.connecting_source is not None and self.connecting_source != node_id:
            source = self.nodes[self.connecting_source]
            target = self.nodes[node_id]
            
            # Add connection
            if target not in source.connections:
                source.connections.append(target)
                self.draw_connection(source, target)
            
            # Reset connecting state
            self.connecting_source = None
            self.canvas.config(cursor='arrow')
    
    def on_text_changed(self, node_id: int):
        """Handle text changes in a node"""
        node = self.nodes[node_id]
        if node.text_widget:
            node.title = node.text_widget.get('1.0', 'end-1c')
    
    def on_double_click(self, event):
        """Handle double click to focus text widget"""
        clicked_items = self.canvas.find_overlapping(event.x-2, event.y-2, event.x+2, event.y+2)
        for item in clicked_items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith('node'):
                    node_id = int(tag[4:])
                    node = self.nodes[node_id]
                    if node.text_widget:
                        node.text_widget.focus_set()
                    break
    
    def on_drag(self, event):
        """Handle drag event"""
        if self.selected_node is not None and not self.resize_mode:
            node = self.nodes[self.selected_node]
            
            # Update node position
            node.x = event.x
            node.y = event.y
            
            # Update node graphics
            self.redraw_node(self.selected_node)
            self.update_connections()
    
    def on_release(self, event):
        """Handle mouse release event"""
        self.resize_mode = False
        self.resize_start = None
    
    def start_connecting(self):
        """Start connecting nodes mode"""
        if self.selected_node is not None:
            self.connecting_source = self.selected_node
            self.canvas.config(cursor='cross')
    
    def update_connections(self):
        """Update all connection lines"""
        # Clear existing lines
        for item in self.canvas.find_all():
            if self.canvas.type(item) == 'line':
                self.canvas.delete(item)
        
        # Redraw all connections
        for node in self.nodes.values():
            for target in node.connections:
                self.draw_connection(node, target)
    
    def clear_all(self):
        """Clear the entire mind map"""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear the entire mind map?"):
            self.canvas.delete('all')
            self.nodes.clear()
            self.next_node_id = 1
            self.selected_node = None
            self.connecting_source = None

    def on_canvas_click(self, event):
        """Handle canvas click event"""
        # If clicked on empty space, deselect current node
        clicked_items = self.canvas.find_overlapping(event.x-2, event.y-2, event.x+2, event.y+2)
        if not clicked_items:
            if self.selected_node is not None:
                self.canvas.itemconfig(f'box{self.selected_node}', outline='black')
                self.selected_node = None
    
    def on_right_click(self, event):
        """Handle right click event"""
        # Check if clicked on a node
        clicked_items = self.canvas.find_overlapping(event.x-2, event.y-2, event.x+2, event.y+2)
        node_id = None
        
        for item in clicked_items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith('node'):
                    node_id = int(tag[4:])
                    break
            if node_id is not None:
                break
        
        # Create context menu
        menu = tk.Menu(self.root, tearoff=0)
        
        if node_id is not None:
            # Node-specific options
            self.select_node(node_id)
            menu.add_command(label="Change Color", command=lambda: self.change_node_color(node_id))
            menu.add_separator()
        
        # Always show Add Node option
        menu.add_command(label="Add Node", command=lambda: self.add_node(event.x, event.y))
        
        # Show menu
        menu.post(event.x_root, event.y_root)

    def change_node_color(self, node_id: int):
        """Change the color of a node"""
        node = self.nodes[node_id]
        color = colorchooser.askcolor(color=node.color)[1]
        if color:
            node.color = color
            self.canvas.itemconfig(f'box{node_id}', fill=color)
            if node.text_widget:
                node.text_widget.configure(bg=color)

def main():
    root = tk.Tk()
    app = MindMapApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()