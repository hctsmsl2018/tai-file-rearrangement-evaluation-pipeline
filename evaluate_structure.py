from pathlib import Path
import zss

GROUND_TRUTH_PATH = Path("GroundTruth")
PREDICTION_PATH = Path("Prediction")

# Top down: only consider folder
# Bottom up: files too, only consider up to certain level
# Use precision/recall/f1 instead of edit distance

def build_tree(path, depth_limit, current_depth=0, ignore_names=True):
    if current_depth >= 3:
        return zss.Node(path.name)

    node = zss.Node(path.name)

    for item in sorted(path.iterdir(), key=lambda x: x.name):
        if item.is_dir():
            child_node = build_tree(item, current_depth - 1, ignore_names=ignore_names)
        else: 
            child_node = zss.Node("." if ignore_names else item.name)

        node.addkid(child_node)
        
    return node

def find_structure_similarity(depth_limit=3, ignore_names=True):
    ground_truth_tree = build_tree(GROUND_TRUTH_PATH, depth_limit, ignore_names=ignore_names)
    prediction_tree = build_tree(PREDICTION_PATH, depth_limit, ignore_names=ignore_names)

    curr_ground_truth_children = [ground_truth_tree]
    curr_prediction_children = [prediction_tree]
    
    for depth in range(depth_limit):
        next_ground_truth_children = []
        ground_truth_layer_structure = zss.Node(".")

        for node in curr_ground_truth_children:
            for child in node.children:
                next_ground_truth_children.append(child)
                ground_truth_layer_structure.addkid(child)

        next_prediction_children = []
        prediction_layer_structure = zss.Node(".")

        for node in curr_prediction_children:
            for child in node.children:
                next_prediction_children.append(child)
                prediction_layer_structure.addkid(child)

        similarity = zss.simple_distance(ground_truth_layer_structure, prediction_layer_structure)

        print(f"Edit Distance (up to depth {depth + 1}): {similarity:.4f}")

        curr_ground_truth_children = next_ground_truth_children
        curr_prediction_children = next_prediction_children

if __name__ == "__main__":
    find_structure_similarity(ignore_names=False)