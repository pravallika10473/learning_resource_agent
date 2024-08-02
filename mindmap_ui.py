import tkinter as tk
from tkinter import ttk

class MindMapNode:
    def __init__(self, text, children=None):
        self.text = text
        self.children = children if children is not None else []

class MindMapApp:
    def __init__(self, root, mind_map_structure):
        self.root = root
        self.root.title("Mind Map UI")
        
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600, scrollregion=(0, 0, 2000, 2000))
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.vbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hbar = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        
        self.create_mind_map(mind_map_structure, 400, 50, 200, 150)
        
    def create_node(self, text, x, y):
        node = self.canvas.create_text(x, y, text=text, font=("Arial", 12), fill="black", tags="node")
        bbox = self.canvas.bbox(node)
        rect = self.canvas.create_rectangle(bbox, outline="black", fill="lightgrey", tags="rect")
        self.canvas.tag_lower(rect, node)
        return node
    
    def create_sub_nodes(self, parent_node, children, x_offset, y_offset):
        parent_bbox = self.canvas.bbox(parent_node)
        parent_x = (parent_bbox[0] + parent_bbox[2]) / 2
        parent_y = (parent_bbox[1] + parent_bbox[3]) / 2
        
        for i, child in enumerate(children):
            sub_node = self.create_node(child.text, parent_x + x_offset, parent_y + y_offset * (i + 1))
            self.canvas.create_line(parent_x, parent_y, parent_x + x_offset, parent_y + y_offset * (i + 1), arrow=tk.LAST)
            if child.children:
                self.create_sub_nodes(sub_node, child.children, x_offset, y_offset / 2)

    def create_mind_map(self, structure, x, y, x_offset, y_offset):
        central_node = self.create_node(structure.text, x, y)
        self.create_sub_nodes(central_node, structure.children, x_offset, y_offset)

if __name__ == "__main__":
    # Define the mind map structure
    mind_map_structure = MindMapNode("Sci-Fi Writing", [
        MindMapNode("World-Building", [
            MindMapNode("Geography & Environment", [
                MindMapNode("Learn about different planetary ecosystems"),
                MindMapNode("Study climate science and its impact on civilizations")
            ]),
            MindMapNode("Societies & Cultures", [
                MindMapNode("Research historical civilizations and their structures"),
                MindMapNode("Understand social dynamics and cultural evolution")
            ]),
            MindMapNode("Technology & Innovation", [
                MindMapNode("Explore cutting-edge technologies and their potential future developments"),
                MindMapNode("Study the history of technological advancements")
            ])
        ]),
        MindMapNode("Character Development", [
            MindMapNode("Psychology", [
                MindMapNode("Learn basic psychology to create realistic characters"),
                MindMapNode("Study personality types and human behavior")
            ]),
            MindMapNode("Relationships", [
                MindMapNode("Understand different types of relationships and their dynamics"),
                MindMapNode("Explore how relationships evolve over time")
            ]),
            MindMapNode("Motivations & Conflicts", [
                MindMapNode("Learn about different types of motivations (intrinsic vs. extrinsic)"),
                MindMapNode("Study conflict resolution and its narrative importance")
            ])
        ]),
        MindMapNode("Plot Structure", [
            MindMapNode("Story Arcs", [
                MindMapNode("Learn about different types of story arcs (e.g., Hero’s Journey, Three-Act Structure)"),
                MindMapNode("Study successful sci-fi plots for inspiration")
            ]),
            MindMapNode("Pacing", [
                MindMapNode("Understand the importance of pacing in storytelling"),
                MindMapNode("Learn techniques to maintain reader interest")
            ]),
            MindMapNode("Twists & Turns", [
                MindMapNode("Study famous plot twists and their impact"),
                MindMapNode("Learn how to foreshadow effectively")
            ])
        ]),
        MindMapNode("Science Fundamentals", [
            MindMapNode("Physics", [
                MindMapNode("Learn basic principles of physics (e.g., relativity, quantum mechanics)"),
                MindMapNode("Study how these principles can be applied in a sci-fi context")
            ]),
            MindMapNode("Biology", [
                MindMapNode("Understand human biology and potential future evolutions"),
                MindMapNode("Explore xenobiology and the possibilities of alien life forms")
            ]),
            MindMapNode("Astronomy", [
                MindMapNode("Learn about the universe, galaxies, and celestial bodies"),
                MindMapNode("Study space travel and its challenges")
            ])
        ]),
        MindMapNode("Writing Techniques", [
            MindMapNode("Style & Voice", [
                MindMapNode("Develop a unique writing style and voice"),
                MindMapNode("Study different narrative styles and their effects")
            ]),
            MindMapNode("Dialogue", [
                MindMapNode("Learn how to write realistic and engaging dialogue"),
                MindMapNode("Study dialogue from successful sci-fi works")
            ]),
            MindMapNode("Editing & Revision", [
                MindMapNode("Understand the importance of editing and revising"),
                MindMapNode("Learn techniques for self-editing and seeking feedback")
            ])
        ]),
        MindMapNode("Inspiration & Research", [
            MindMapNode("Classic Sci-Fi Works", [
                MindMapNode("Read classic sci-fi literature for inspiration"),
                MindMapNode("Study the themes and techniques used by renowned authors")
            ]),
            MindMapNode("Current Trends", [
                MindMapNode("Stay updated with current trends in sci-fi"),
                MindMapNode("Explore new and emerging sub-genres")
            ]),
            MindMapNode("Cross-Disciplinary Learning", [
                MindMapNode("Learn from other fields (e.g., philosophy, sociology, anthropology)"),
                MindMapNode("Understand how these fields can enrich sci-fi writing")
            ])
        ])
    ])

    root = tk.Tk()
    app = MindMapApp(root, mind_map_structure)
    root.mainloop()
