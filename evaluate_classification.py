from pathlib import Path
from hashlib import file_digest

GROUND_TRUTH_PATH = Path("GroundTruth")
PREDICTION_PATH = Path("Prediction")

ROOT_PATH = Path(".")

class File:
    def __init__(self, path, file_hash=None):
        self.path = create_path_repr(path)

        if file_hash is None:
            with open(path, "rb") as f:
                file_hash = file_digest(f, "sha256").hexdigest()
        print(path, file_hash)
        self.hash = hash(file_hash)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __str__(self):
        return str(self.path)
    
    def __repr__(self):
        return f"File({self.path})"

def create_path_repr(path):
    if len(path.parts) > 0 and path.parts[0] == "C:\\":
        path = Path(*path.parts[1:])

    return path

def evaluate_folder(ground_truth_folder_data, prediction_folder_data, folder_path=ROOT_PATH, ignore_files=False, limit=3):
    item_to_check = "subfolders" if ignore_files else "files"

    ground_truth_folder_content = ground_truth_folder_data[folder_path][item_to_check]
    
    true_labels = len(ground_truth_folder_content)

    children = []

    if folder_path in prediction_folder_data:
        prediction_folder_content = prediction_folder_data[folder_path][item_to_check]

        false_positives = [str(path) for path in prediction_folder_content - ground_truth_folder_content]
        false_negatives = [str(path) for path in ground_truth_folder_content - prediction_folder_content]

        true_positives = len(ground_truth_folder_content & prediction_folder_content)
        positives = len(prediction_folder_content)

        eval_recursively = len(folder_path.parts) != limit - 1

        if eval_recursively:
            for subfolder in ground_truth_folder_data[folder_path]["subfolders"]:
                tp, t_labels, pos, folder_info = evaluate_folder(ground_truth_folder_data, prediction_folder_data, folder_path=subfolder, ignore_files=ignore_files, limit=limit)

                true_positives += tp
                true_labels += t_labels
                positives += pos
                children.append(folder_info)
    else:
        true_positives = 0
        positives = 0

    precision = true_positives / positives if positives > 0 else 0
    recall = true_positives / true_labels if true_labels > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if {precision, recall} != {0} else 0
    
    folder_info = {"folder": str(folder_path), "precision": precision, "recall": recall, "f1": f1}

    correctly_arranged = precision == 1 and recall == 1 or folder_path in prediction_folder_data and len(ground_truth_folder_content) == 0 and len(prediction_folder_content) == 0

    if len(children) != 0:
        folder_info["children"] = "Children are excluded as this subfolder is correctly arranged" if correctly_arranged else children

    if folder_path in prediction_folder_data and not correctly_arranged:
        folder_info["false_positives"] = false_positives
        folder_info["false_negatives"] = false_negatives

    return true_positives, true_labels, positives, folder_info

def create_folder_children_dict(path, output):
    path_repr = create_path_repr(path)

    output[path_repr] = {"files": set(), "subfolders": set()}

    for item in path.iterdir():
        if item.is_file() and item.suffix != ".yaml":
            output[path_repr]["files"].add(File(item))
        elif item.is_dir():
            output[path_repr]["subfolders"].add(create_path_repr(item))

            create_folder_children_dict(item, output)

def precision_recall_f1(ground_truth_path, prediction_path, ignore_files=False):
    ground_truth_dict_tree = {}
    prediction_dict_tree = {}
    
    create_folder_children_dict(ground_truth_path, ground_truth_dict_tree)
    create_folder_children_dict(prediction_path, prediction_dict_tree)

    evaluate_folder(ground_truth_dict_tree, prediction_dict_tree, ignore_files=ignore_files)

if __name__ == "__main__":
    precision_recall_f1(GROUND_TRUTH_PATH, PREDICTION_PATH, ignore_files=True)