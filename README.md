# Rearrangement Evaluation

This project contains evaluation scripts for comparing ground truth folder structures against predicted folder structures.

## Scripts

### evaluate_structure_v2.py

Evaluates folder structure predictions using either a top-down or bottom-up approach.

#### Usage

```bash
python evaluate_structure_v2.py --ground-truth <path> --prediction <path>
```

#### Arguments

- `--ground-truth`, `-g` (required): Path to the ground truth folder for evaluation
- `--prediction`, `-p` (required): Path to the prediction folder for evaluation
- `--method`, `-m` (optional): Method of evaluation: `top_down` or `bottom_up` (default: `bottom_up`)
- `--limit`, `-l` (optional): Number of parent levels to compare (bottom-up) or folder depth to consider (top-down). This controls how many ancestor folders nearest to a file are compared (default: `3`).

#### Example

```bash
python evaluate_structure_v2.py --ground-truth "CS 61A - Ground truth" --prediction "CS 61A - Prediction"
```

Using the top-down evaluation method:

```bash
python evaluate_structure_v2.py --ground-truth "CS 61A - Ground truth" --prediction "CS 61A - Prediction" --method top_down
```

Or using short flags:

```bash
python evaluate_structure_v2.py -g "CS 61A - Ground truth" -p "CS 61A - Prediction" -m bottom_up
```

Specify the comparison depth with `--limit` (or `-l`):

```bash
python evaluate_structure_v2.py -g "CS 61A - Ground truth" -p "CS 61A - Prediction" -m bottom_up -l 2
```

### evaluate_classification.py

Evaluates folder structure predictions and reports precision, recall, and F1 scores.

#### Usage

```bash
python evaluate_classification.py
```

This script uses the default paths defined in the constants:
- `GROUND_TRUTH_PATH = Path("GroundTruth")`
- `PREDICTION_PATH = Path("Prediction")`

## Output

Both evaluation scripts produce metrics including:
- **Precision**: The proportion of predicted items that were correct
- **Recall**: The proportion of ground truth items that were correctly identified
- **F1 Score**: The harmonic mean of precision and recall

Metrics are reported at both folder and global levels.

**Evaluation Details**

- **Top-down (precision & recall):** Correctness is defined as a file or folder being placed at the exact correct file path. The `limit` argument controls the folder depth considered for top-down evaluation (i.e., how deep into the folder hierarchy rearrangements are evaluated). Precision measures the proportion of predicted placements that are exactly correct (i.e., how many predicted file paths match the ground truth). Recall measures the proportion of ground-truth placements that were predicted correctly (i.e., how many ground-truth file paths were recovered by the prediction). These metrics can be reported per-folder (by considering items within a folder) or globally (root-level aggregate).

- **Bottom-up (accuracy):** Accuracy is measured by comparing a fixed number of the nearest parent folders for each file. The `limit` argument passed to `evaluate_tree()` controls how many parent levels (closest to the file) are compared. For each file, up to `limit` parent folders are examined and the number of matching parent names between prediction and ground truth is counted; accuracy is the total number of matching parent comparisons divided by the total number of parent comparisons performed. This gives a graded measure of how close predicted parentage is to the ground truth even when the file is not placed at the exact correct path.
