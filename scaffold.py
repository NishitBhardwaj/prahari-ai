import os
from pathlib import Path

base_dir = Path("dataset-generator")
directories = [
    "configs",
    "raw_data",
    "etl",
    "master",
    "geography",
    "engines/population_engine",
    "engines/activity_engine",
    "engines/social_engine",
    "engines/time_engine",
    "engines/timeline_engine",
    "engines/scenario_engine",
    "engines/crime_engine",
    "engines/behaviour_engine",
    "engines/gang_engine",
    "engines/victimization_engine",
    "engines/witness_engine",
    "engines/communication_engine",
    "engines/finance_engine",
    "engines/mobility_engine",
    "engines/evidence_engine",
    "engines/cctv_engine",
    "engines/features_engine",
    "engines/risk_engine",
    "media/images",
    "media/videos",
    "media/audio",
    "media/documents",
    "media/forensics",
    "media/fingerprints",
    "media/dna",
    "media/cctv",
    "validation",
    "exports",
    "tests",
    "docs"
]

for d in directories:
    dir_path = base_dir / d
    dir_path.mkdir(parents=True, exist_ok=True)
    init_file = dir_path / "__init__.py"
    if not init_file.exists() and not d.startswith("media/") and d not in ["configs", "raw_data", "docs"]:
        init_file.touch()

(base_dir / "__init__.py").touch()
(base_dir / "engines/__init__.py").touch()
print("Scaffolding complete.")
