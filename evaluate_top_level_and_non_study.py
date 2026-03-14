from pathlib import Path
import json

from evaluate_classification import File

"""
Team 1: top-level categories, structure for folders other than study
Team 2: study structure

For items/parts that are fully accurate, no need to print
"""

def construct_tree_from_json():
    with open("bfs_v3_tree.json") as f:
        bfs_result = json.load(f)

    tree = {}

    def _build_tree(folder):
        folder_path = Path(folder["path"])
        files = {File(Path(file_hash), info["path"]) for file_hash, info in folder["files"].items()}
        print(folder.keys())
        subfolders = set()

        for info in folder["children"].values():
            subfolders.add(Path(info["path"]))
            _build_tree(info)

        tree[folder_path] = {"files": files, "subfolders": subfolders}

    _build_tree(bfs_result)

    return tree

def main():
    prediction = construct_tree_from_json()
    print(prediction)

if __name__ == "__main__":
    main()