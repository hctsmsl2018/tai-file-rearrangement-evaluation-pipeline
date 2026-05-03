from pathlib import Path
import argparse
import pickle
import json
from contextlib import chdir

from evaluate_classification import evaluate_folder, create_folder_children_dict, ROOT_PATH, PREDICTION_PATH

'''
1/28

Top down:

-Analyze everything top-down
-If bottom up is good, top down can just consider folders

Bottom up:

-Check if a # of parents are correct for a file (e.g. 3)

Add README:

-What does high precision/low recall mean? What about with respect to top down/bottom up?
-Nice to have: an example

2/4

Top down for 1 level from one specific folder
'''

def get_top_down_files(children_dict, limit):
    return {path: {"files": content["files"], "subfolders": set() if len(path.parts) == limit else content["subfolders"]} for path, content in children_dict.items() if len(path.parts) <= limit}

def get_bottom_up_score(ground_truth_dict, prediction_dict, limit):
    prediction_files = {file:file.path for children in prediction_dict.values() for file in children["files"]}
    #print(prediction_files)
    ground_truth_file_to_prediction_path = {file: prediction_files[file] for children in ground_truth_dict.values() for file in children["files"]}

    def _get_folder_score(folder, limit):
        children = ground_truth_dict[folder]

        total = 0
        correct = 0

        incorrect_paths = []
        
        for file in children["files"]:
            prediction_path = ground_truth_file_to_prediction_path[file]

            if folder == Path("."):
                total += 1

                curr_file_correct = len(prediction_path.parts) == 1

                correct += int(curr_file_correct)

                if not curr_file_correct:
                    incorrect_paths.append(str(prediction_path))
            else:
                ground_truth_comparison_len = min(limit, len(folder.parts))
                prediction_comparison_len = min(ground_truth_comparison_len, len(prediction_path.parts) - 1)

                total += ground_truth_comparison_len

                comparison_start_ind = -prediction_comparison_len - 1

                ground_truth_to_compare = folder.parts[-prediction_comparison_len:]
                predictions_to_compare = prediction_path.parts[comparison_start_ind:-1]

                num_parts_correct = sum(g == p for g, p in zip(ground_truth_to_compare, predictions_to_compare))

                correct += num_parts_correct

                if ground_truth_comparison_len != num_parts_correct:
                    incorrect_paths.append(str(prediction_path))

        children_acc_info = []

        for subfolder in children["subfolders"]:
            total_cont, correct_cont, subfolder_info = _get_folder_score(subfolder, limit)
            
            total += total_cont
            correct += correct_cont
            children_acc_info.append(subfolder_info)

        folder_info = {"folder": str(folder)}

        if total != 0:
            accuracy = correct / total
            folder_info["accuracy"] = accuracy

        if len(incorrect_paths) != 0:
            folder_info["incorrect_paths"] = incorrect_paths

        if len(children_acc_info) != 0:
            folder_info["children"] = "Children are excluded as this subfolder is correctly arranged" if total == correct else children_acc_info

        return total, correct, folder_info

    *_, eval_info = _get_folder_score(Path('.'), limit)
    return eval_info

def build_tree_from_files(path):
    cache_file = Path(f"file_tree_reprs/tree_{str(path)}.pkl")

    if cache_file.exists():
        with open(cache_file, "rb") as f:
            tree = pickle.load(f)
    else:
        tree = {}

        with chdir("test_arrangements" / path):
            create_folder_children_dict(Path("."), tree)

        with open(cache_file, "wb") as f:
            pickle.dump(tree, f)

    return tree

def evaluate_tree(ground_truth_path, prediction_path, ground_truth_tree, prediction_tree, method, limit=3):
    if method == "top_down":
        ground_truth_layers = get_top_down_files(ground_truth_tree, limit)
        prediction_layers = get_top_down_files(prediction_tree, limit)

        *_, evaluation_report = evaluate_folder(ground_truth_layers, prediction_layers, folder_path=ROOT_PATH, ignore_files=True, limit=3)
    elif method == "bottom_up":
        evaluation_report = get_bottom_up_score(ground_truth_tree, prediction_tree, limit)

    with open(f"evaluation_reports/{str(ground_truth_path)}_{str(prediction_path)}_{method}.json", "w") as f:
        json.dump(evaluation_report, f, indent=2)

def create_and_evaluate_trees(ground_truth_path, prediction_path, method, limit=3):
    ground_truth_tree = build_tree_from_files(ground_truth_path)
    prediction_tree = build_tree_from_files(prediction_path)

    evaluate_tree(ground_truth_path, prediction_path, ground_truth_tree, prediction_tree, method, limit)

def main():
    parser = argparse.ArgumentParser(description="Evaluate folder structure prediction accuracy")
    parser.add_argument(
        "--ground-truth", "-g",
        required=True,
        help="Path to the ground truth folder for evaluation"
    )
    parser.add_argument(
        "--prediction", "-p",
        required=True,
        help="Path to the prediction folder for evaluation"
    )
    parser.add_argument(
        "--method", "-m",
        required=False,
        choices=["top_down", "bottom_up"],
        default="bottom_up",
        help="Method of evaluation: top_down or bottom_up (default: bottom_up)"
    )
    parser.add_argument(
        "--limit", "-l",
        required=False,
        type=int,
        default=3,
        help="Number of parent levels to compare (bottom-up) or folder depth to consider (top-down) (default: 3)"
    )
    
    args = parser.parse_args()
    
    create_and_evaluate_trees(Path(args.ground_truth), Path(args.prediction), method=args.method, limit=args.limit)

if __name__ == "__main__":
    main()