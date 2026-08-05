# Dataset Directory

This directory holds ECG report images for training, validation, and testing the Smart Ambulance AI classifier.

---

## ⚠️ Important Context

> **This system analyses photographs of printed ECG reports captured using a camera (e.g., from an ambulance tablet or phone). It does NOT process raw ECG sensor signals.**

The model must learn to handle:
- Variable lighting (ambulance interior, daylight, flash)
- Camera angle and slight rotation
- Paper texture and print quality variation
- Motion blur from a moving vehicle

---

## Directory Structure

```
dataset/
├── train/               ← 70–80% of labelled images
│   ├── normal/
│   ├── possible_stemi/
│   └── needs_review/
│
├── validation/          ← 10–15% for hyperparameter tuning
│   ├── normal/
│   ├── possible_stemi/
│   └── needs_review/
│
└── test/                ← 10–15% held-out set for final evaluation
    ├── normal/
    ├── possible_stemi/
    └── needs_review/
```

---

## Class Definitions

| Folder name | Description |
|---|---|
| `normal` | ECG report with no significant abnormality |
| `possible_stemi` | ECG showing signs of ST-elevation myocardial infarction |
| `needs_review` | Abnormal ECG that requires cardiologist review but is not definitively STEMI |

---

## Image Requirements

| Property | Requirement |
|---|---|
| Format | JPG / JPEG / PNG |
| Minimum resolution | 224 × 224 px (higher is better, will be resized) |
| Channels | RGB (colour photos preferred) |
| Content | Full ECG strip visible; avoid cropping leads |
| Labelling | Must be verified by a licensed cardiologist or clinical ECG expert |

---

## Recommended Split

| Split | Proportion | Minimum images per class |
|---|---|---|
| train | 70% | 50 |
| validation | 15% | 15 |
| test | 15% | 15 |

---

## Naming Convention

Use descriptive filenames — do not use patient identifiers:

```
normal_001.jpg
possible_stemi_042.png
needs_review_017.jpeg
```

---

## ⚠️ Clinical Disclaimer

> **This is a prototype ECG image classification system.**
> It requires a properly labelled clinical dataset reviewed by licensed cardiologists
> for real-world medical validation. Do not use model predictions as the sole basis
> for any clinical decision.

---

## Populating This Directory

1. Collect de-identified ECG report photographs.
2. Have each image labelled by a qualified clinician.
3. Place images in the appropriate `train/`, `validation/`, and `test/` subfolders.
4. Run `python model/train.py` from the `ai/` directory.

**The model will NOT be trained automatically when the API starts.**
Training must be triggered manually using `model/train.py`.
