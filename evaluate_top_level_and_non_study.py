from pathlib import Path
import json

from evaluate_classification import File
from evaluate_structure_v2 import build_tree_from_files, evaluate_tree

"""
Team 1: top-level categories, structure for folders other than study
-Plan to send output template
Team 2: study structure
-Only need to focus on evaluation of lecture group

For items/parts that are fully accurate, no need to print

4/1:

Evaluation:
-From DB, compare relative_path and updated_path
-Aggregated metrics for each pair of paths: exact match, first top-down mismatch, first bottom-up mismatch
"""

def construct_top_level_non_study_tree_from_json():
    with open("test_arrangements/bfs_v3_tree.json") as f:
        bfs_result = json.load(f)

    tree = {}

    def _build_tree(folder):
        folder_path = Path(folder["path"])
        files = {File(Path(info["path"]), file_hash): info["category"] for file_hash, info in folder["files"].items()} if "files" in folder else {}

        subfolders = set()

        if "children" in folder:
            for info in folder["children"].values():
                subfolders.add(Path(info["path"]))
                _build_tree(info)

        tree[folder_path] = {"files": files, "subfolders": subfolders}

    _build_tree(bfs_result)

    return tree

def construct_study_tree_from_json():
    with open("test_arrangements/rearrangement_structure_tree.json") as f:
        bfs_result = json.load(f)

    tree = {}

    def _build_tree(folder):
        for item in folder:
            if item["type"] == "file":
                pass
            elif item["type"] == "folder":
                pass
            if "children" in item:
                _build_tree(item["children"])
        folder_path = Path(folder["path"])
        files = {File(Path(info["path"]), file_hash): info["category"] for file_hash, info in folder["files"].items()} if "files" in folder else {}
  
        subfolders = set()

        if "children" in folder:
            for info in folder["children"].values():
                subfolders.add(Path(info["path"]))
                _build_tree(info)

        tree[folder_path] = {"files": files, "subfolders": subfolders}

    _build_tree(bfs_result)

    return tree

def main():
    ground_truth_path = Path("CS 61A - Ground truth")

    ground_truth_tree = build_tree_from_files(ground_truth_path)
    prediction_tree = construct_top_level_non_study_tree_from_json()
    
    evaluate_tree(ground_truth_path, "bfs_v3_tree.json", ground_truth_tree, prediction_tree, method="bottom_up")

if __name__ == "__main__":
    main()