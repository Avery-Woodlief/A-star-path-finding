# Pathfinding Visualization Tools

This project contains two primary utilities:

* **`map_maker.py`** – Create and edit obstacle maps.
* **`visualization.py`** – Visualize pathfinding behavior using the `Navigator` class.

---

# Map Maker (`map_maker.py`)

Use the map maker to create obstacle layouts that can be exported and later loaded by the pathfinding visualizer.

## Controls

| Action                        | Control                                        |
| ----------------------------- | ---------------------------------------------- |
| Create a rectangular obstacle | **Press and hold Right Mouse Button** and drag |
| Undo last obstacle            | **Left Ctrl + Z**                              |
| Enable edit mode              | **Left Shift + E**                             |
| Move an obstacle (edit mode)  | **Click and drag** a rectangle                 |
| Quit map maker                | **Escape**                                     |

## Exporting

When you exit the map maker, you will be prompted to provide a map name.

The current obstacle layout will then be exported as a **JSON** file for later use.

---

# Pathfinding Visualization (`visualization.py`)

Use the visualizer to experiment with and observe the behavior of the `Navigator` pathfinding algorithm.

## Controls

| Action                 | Control                |
| ---------------------- | ---------------------- |
| Set a **Start** anchor | **Left Mouse Button**  |
| Set an **End** anchor  | **Right Mouse Button** |
| Toggle Navigator       | **Left Ctrl + S**      |

Once both a **Start** and **End** anchor have been placed (in either order), the `Navigator` will begin computing a path.

---

## Creating Disjoint Paths

To create multiple independent paths without connecting them together:

1. Allow the current path to finish.
2. Press **Left Ctrl + S** to disable the Navigator.
3. Place a new **End** anchor.
4. Press **Left Ctrl + S** again to re-enable the Navigator.
5. Place a new **Start** anchor.

You may also reverse the order of the Start and End anchors.

This workflow prevents the Navigator from immediately linking the new path to a previously completed one.

---

# Notes

* Maps are stored as JSON files.
* Obstacles are represented as rectangles.
* The visualizer can be used to test pathfinding behavior on exported maps.
* Start and End anchors may be placed in either order.

