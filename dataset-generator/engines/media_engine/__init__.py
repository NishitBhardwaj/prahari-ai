"""
Media Asset Generation Engine — generates REAL synthetic media files, not just metadata.

Generates:
  1. Synthetic profile images (people — accused, victims, officers)
  2. Vehicle images (colored silhouettes with registration plates)
  3. Crime scene images (composited evidence scenes)
  4. CCTV frame images (timestamped surveillance frames)
  5. Evidence images (weapons, drugs, phones, cash)
  6. Fingerprint images (synthetic ridge patterns)
  7. Signature images (synthetic handwriting strokes)
  8. Official PDF documents (FIR, Chargesheet, Arrest Memo, Court Order)
  9. Map heatmaps (district crime density)

Two modes:
  - Development: generates media for a configurable subset (1-5% of entities)
  - Production: generates media for all entities (use with batch workers)

Depends on: master, population, police, crime (if available), evidence (if available)
"""

import os
import math
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from pathlib import Path
from io import BytesIO

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from loguru import logger

from engines.base_engine import BaseEngine
from schemas.base import generate_id
from configs.config_loader import PlatformConfig

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


# ──────────────────────────────────────────────
# Color palettes for synthetic generation
# ──────────────────────────────────────────────
SKIN_TONES = [
    (198, 164, 131), (180, 140, 100), (160, 120, 80),
    (140, 100, 65),  (120, 85, 55),   (100, 70, 45),
    (220, 185, 155), (210, 175, 140), (190, 155, 115),
]

HAIR_COLORS = [
    (20, 15, 10), (40, 30, 20), (60, 45, 30),
    (80, 55, 35), (100, 70, 45), (30, 25, 20),
]

SHIRT_COLORS = [
    (220, 220, 230), (180, 200, 220), (200, 180, 160),
    (160, 180, 200), (180, 160, 140), (100, 120, 160),
    (140, 80, 80),   (80, 120, 80),   (200, 200, 180),
    (240, 240, 240),  # White (for police)
    (50, 60, 80),     # Dark blue (for police)
    (70, 80, 60),     # Khaki (for police)
]

VEHICLE_COLORS_RGB = {
    "White": (240, 240, 240), "Silver": (192, 192, 192), "Black": (30, 30, 30),
    "Grey": (128, 128, 128), "Red": (180, 40, 40), "Blue": (40, 60, 160),
    "Brown": (120, 80, 40), "Green": (40, 120, 60), "Yellow": (220, 200, 40),
    "Orange": (220, 130, 40), "Maroon": (100, 20, 30),
}

EVIDENCE_TYPES_VISUAL = {
    "Knife": {"bg": (60, 60, 70), "shape": "blade", "label_color": (255, 80, 80)},
    "Pistol": {"bg": (50, 50, 60), "shape": "gun", "label_color": (255, 100, 100)},
    "Mobile": {"bg": (40, 40, 50), "shape": "rect", "label_color": (100, 200, 255)},
    "Laptop": {"bg": (45, 45, 55), "shape": "rect_wide", "label_color": (100, 200, 255)},
    "Cash": {"bg": (30, 60, 30), "shape": "bundle", "label_color": (100, 255, 100)},
    "Drug": {"bg": (70, 50, 50), "shape": "packet", "label_color": (255, 150, 50)},
    "Document": {"bg": (60, 60, 65), "shape": "paper", "label_color": (200, 200, 255)},
}


class MediaEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "media"

    @property
    def dependencies(self) -> List[str]:
        return ["master", "population", "police"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Starting Media Asset Generation Engine...")

        # Determine generation percentage based on mode
        # Development mode: generate for 3% of entities
        # Production mode: generate for all (controlled via config)
        total_persons = len(self.store.get("persons"))
        total_employees = len(self.store.get("employees"))

        media_percentage = 0.03  # 3% in development mode
        n_person_images = max(20, int(total_persons * media_percentage))
        n_officer_images = max(10, int(total_employees * media_percentage))

        # Create media directories
        media_base = Path(self.output_dir) / "media"
        dirs = {
            "profiles_accused": media_base / "images" / "accused",
            "profiles_victims": media_base / "images" / "victims",
            "profiles_officers": media_base / "images" / "officers",
            "profiles_complainants": media_base / "images" / "complainants",
            "vehicles": media_base / "images" / "vehicles",
            "evidence": media_base / "images" / "evidence",
            "crime_scenes": media_base / "images" / "crime_scenes",
            "cctv_frames": media_base / "images" / "cctv",
            "fingerprints": media_base / "forensics" / "fingerprints",
            "signatures": media_base / "forensics" / "signatures",
            "documents": media_base / "documents",
            "thumbnails": media_base / "thumbnails",
            "maps": media_base / "maps",
        }
        for d in dirs.values():
            d.mkdir(parents=True, exist_ok=True)

        all_media_records = []

        # 1. Generate person profile images
        persons = self.store.get("persons")
        employees = self.store.get("employees")

        self.logger.info(f"Generating {n_person_images} person profile images...")
        person_sample = persons.sample(n=min(n_person_images, len(persons)), random_state=self.config.seed)
        for _, person in person_sample.iterrows():
            record = self._generate_person_image(person, dirs)
            if record:
                all_media_records.append(record)

        # 2. Generate officer images
        self.logger.info(f"Generating {n_officer_images} officer profile images...")
        officer_sample = employees.sample(n=min(n_officer_images, len(employees)), random_state=self.config.seed)
        for _, officer in officer_sample.iterrows():
            record = self._generate_officer_image(officer, dirs)
            if record:
                all_media_records.append(record)

        # 3. Generate vehicle images (20 sample vehicles)
        n_vehicle_images = 20
        self.logger.info(f"Generating {n_vehicle_images} vehicle images...")
        for i in range(n_vehicle_images):
            record = self._generate_vehicle_image(i, dirs)
            all_media_records.append(record)

        # 4. Generate evidence images (one per type)
        self.logger.info("Generating evidence type images...")
        for etype, econfig in EVIDENCE_TYPES_VISUAL.items():
            record = self._generate_evidence_image(etype, econfig, dirs)
            all_media_records.append(record)

        # 5. Generate crime scene images (10 samples)
        self.logger.info("Generating crime scene images...")
        for i in range(10):
            record = self._generate_crime_scene_image(i, dirs)
            all_media_records.append(record)

        # 6. Generate CCTV frames (15 samples)
        self.logger.info("Generating CCTV frame images...")
        for i in range(15):
            record = self._generate_cctv_frame(i, dirs)
            all_media_records.append(record)

        # 7. Generate fingerprint images (10 samples)
        self.logger.info("Generating synthetic fingerprint images...")
        for i in range(10):
            record = self._generate_fingerprint_image(i, dirs)
            all_media_records.append(record)

        # 8. Generate signature images (10 samples)
        self.logger.info("Generating synthetic signature images...")
        for i in range(10):
            record = self._generate_signature_image(i, dirs)
            all_media_records.append(record)

        # 9. Generate crime heatmap (1 per district sample)
        self.logger.info("Generating district crime heatmaps...")
        districts = self.store.get("districts")
        for _, dist in districts.head(5).iterrows():
            record = self._generate_heatmap(dist, dirs)
            all_media_records.append(record)

        # 10. Generate PDF documents (5 sample FIRs)
        if HAS_REPORTLAB:
            self.logger.info("Generating PDF documents...")
            for i in range(5):
                record = self._generate_fir_pdf(i, person_sample, dirs)
                if record:
                    all_media_records.append(record)
        else:
            self.logger.warning("reportlab not installed — skipping PDF generation")

        # Build the full metadata table (for ALL entities, not just generated images)
        media_df = pd.DataFrame(all_media_records)

        # Generate metadata-only records for entities without images
        metadata_only = self._generate_metadata_only_records(persons, employees)

        self.logger.info(
            f"Media engine complete: {len(media_df)} actual media files generated, "
            f"{len(metadata_only)} metadata-only records"
        )

        return {
            "media_assets": media_df,
            "media_metadata_all": pd.concat([media_df, metadata_only], ignore_index=True) if len(metadata_only) > 0 else media_df,
        }

    # ──────────────────────────────────────────────────────
    # 1. Person Profile Images
    # ──────────────────────────────────────────────────────
    def _generate_person_image(self, person: pd.Series, dirs: dict) -> Optional[dict]:
        """Generate a synthetic face image for a person."""
        person_id = person["person_id"]
        gender = person.get("gender", "Male")
        age = person.get("age", 30)

        img = Image.new("RGB", (200, 250), color=(220, 225, 230))
        draw = ImageDraw.Draw(img)

        # Pick colors based on person seed
        seed_val = hash(person_id) % 1000
        skin = SKIN_TONES[seed_val % len(SKIN_TONES)]
        hair = HAIR_COLORS[seed_val % len(HAIR_COLORS)]
        shirt = SHIRT_COLORS[seed_val % len(SHIRT_COLORS)]

        # Background gradient
        for y in range(250):
            r = int(200 + (y / 250) * 30)
            g = int(205 + (y / 250) * 25)
            b = int(215 + (y / 250) * 20)
            draw.line([(0, y), (200, y)], fill=(r, g, b))

        # Neck & shirt
        draw.rectangle([60, 160, 140, 250], fill=shirt)
        draw.ellipse([80, 145, 120, 175], fill=skin)

        # Face (oval)
        face_x, face_y = 100, 110
        face_w, face_h = 50, 60
        draw.ellipse([face_x - face_w, face_y - face_h, face_x + face_w, face_y + face_h], fill=skin)

        # Hair
        hair_style = seed_val % 3
        if hair_style == 0:  # Short hair
            draw.ellipse([face_x - face_w - 3, face_y - face_h - 8, face_x + face_w + 3, face_y - 15], fill=hair)
        elif hair_style == 1:  # Medium hair
            draw.ellipse([face_x - face_w - 5, face_y - face_h - 12, face_x + face_w + 5, face_y - 5], fill=hair)
        else:  # Long hair (more for female)
            draw.ellipse([face_x - face_w - 5, face_y - face_h - 12, face_x + face_w + 5, face_y + 10], fill=hair)
            # Redraw face over hair
            draw.ellipse([face_x - face_w + 2, face_y - face_h + 2, face_x + face_w - 2, face_y + face_h - 2], fill=skin)

        # Eyes
        eye_y = face_y - 10
        draw.ellipse([face_x - 20, eye_y - 4, face_x - 10, eye_y + 4], fill="white")
        draw.ellipse([face_x + 10, eye_y - 4, face_x + 20, eye_y + 4], fill="white")
        draw.ellipse([face_x - 17, eye_y - 2, face_x - 13, eye_y + 2], fill=(40, 30, 20))
        draw.ellipse([face_x + 13, eye_y - 2, face_x + 17, eye_y + 2], fill=(40, 30, 20))

        # Nose
        draw.line([(face_x, face_y - 5), (face_x - 5, face_y + 8), (face_x + 5, face_y + 8)],
                  fill=(skin[0] - 20, skin[1] - 20, skin[2] - 15), width=1)

        # Mouth
        mouth_y = face_y + 20
        draw.arc([face_x - 12, mouth_y - 3, face_x + 12, mouth_y + 8], 0, 180,
                 fill=(180, 80, 80), width=2)

        # Age indicator: wrinkles for older
        if age > 50:
            for _ in range(3):
                wy = face_y + int(self.rng.integers(-30, -15))
                draw.line([(face_x - 25, wy), (face_x - 15, wy + 2)],
                          fill=(skin[0] - 15, skin[1] - 15, skin[2] - 10), width=1)

        # Slight blur for realism
        img = img.filter(ImageFilter.SMOOTH)

        # Determine subdirectory
        subdir = dirs["profiles_accused"]  # default
        filename = f"{person_id}.jpg"
        filepath = subdir / filename
        img.save(str(filepath), "JPEG", quality=85)

        # Generate thumbnail
        thumb = img.resize((50, 63), Image.Resampling.LANCZOS)
        thumb_path = dirs["thumbnails"] / f"thumb_{person_id}.jpg"
        thumb.save(str(thumb_path), "JPEG", quality=70)

        # Compute hash
        with open(str(filepath), "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return {
            "media_id": generate_id("MED-"),
            "entity_type": "Person",
            "entity_id": person_id,
            "media_type": "Image",
            "media_sub_type": "Profile Photo",
            "file_name": filename,
            "storage_path": str(filepath),
            "thumbnail_path": str(thumb_path),
            "file_size_bytes": os.path.getsize(str(filepath)),
            "file_format": "jpg",
            "resolution": "200x250",
            "geotag_latitude": float(person.get("latitude", 0)),
            "geotag_longitude": float(person.get("longitude", 0)),
            "capture_datetime": datetime.now().isoformat(),
            "hash_md5": file_hash,
            "has_file": True,
        }

    # ──────────────────────────────────────────────────────
    # 2. Officer Profile Images
    # ──────────────────────────────────────────────────────
    def _generate_officer_image(self, officer: pd.Series, dirs: dict) -> Optional[dict]:
        """Generate an officer profile with uniform."""
        emp_id = officer["employee_id"]
        rank = officer.get("rank_name", "Constable")

        img = Image.new("RGB", (200, 250), color=(200, 210, 220))
        draw = ImageDraw.Draw(img)

        # Background
        for y in range(250):
            draw.line([(0, y), (200, y)], fill=(190 + y // 10, 195 + y // 12, 210 + y // 15))

        seed_val = hash(emp_id) % 1000
        skin = SKIN_TONES[seed_val % len(SKIN_TONES)]

        # Khaki/Navy uniform
        if "Inspector" in rank or "SP" in rank or "DCP" in rank:
            uniform_color = (50, 60, 80)  # Dark navy
        else:
            uniform_color = (140, 130, 100)  # Khaki

        # Uniform body
        draw.rectangle([55, 155, 145, 250], fill=uniform_color)
        # Collar
        draw.polygon([(75, 155), (100, 170), (125, 155)], fill=(uniform_color[0] + 20, uniform_color[1] + 20, uniform_color[2] + 20))

        # Neck
        draw.ellipse([85, 140, 115, 170], fill=skin)

        # Face
        draw.ellipse([55, 50, 145, 155], fill=skin)

        # Hair
        hair_color = HAIR_COLORS[seed_val % len(HAIR_COLORS)]
        draw.ellipse([52, 42, 148, 100], fill=hair_color)
        draw.ellipse([57, 55, 143, 155], fill=skin)

        # Cap for senior officers
        if "Inspector" in rank or "SP" in rank or "DCP" in rank or "DIG" in rank:
            draw.rectangle([50, 40, 150, 60], fill=(30, 30, 50))
            draw.rectangle([45, 55, 155, 62], fill=(40, 40, 60))

        # Eyes
        draw.ellipse([75, 90, 90, 100], fill="white")
        draw.ellipse([110, 90, 125, 100], fill="white")
        draw.ellipse([80, 92, 87, 98], fill=(30, 25, 20))
        draw.ellipse([115, 92, 122, 98], fill=(30, 25, 20))

        # Nose & Mouth
        draw.line([(100, 100), (96, 115), (104, 115)], fill=(skin[0] - 20, skin[1] - 20, skin[2] - 15), width=1)
        draw.arc([88, 118, 112, 132], 0, 180, fill=(160, 70, 70), width=2)

        # Rank badge (stars/stripes)
        badge_y = 165
        stars = min(3, hash(rank) % 4 + 1)
        for s in range(stars):
            cx = 80 + s * 15
            self._draw_star(draw, cx, badge_y, 5, (220, 180, 50))

        # Name plate
        draw.rectangle([70, 190, 130, 202], fill=(200, 180, 50))

        img = img.filter(ImageFilter.SMOOTH)

        filename = f"{emp_id}.jpg"
        filepath = dirs["profiles_officers"] / filename
        img.save(str(filepath), "JPEG", quality=85)

        thumb = img.resize((50, 63), Image.Resampling.LANCZOS)
        thumb_path = dirs["thumbnails"] / f"thumb_{emp_id}.jpg"
        thumb.save(str(thumb_path), "JPEG", quality=70)

        with open(str(filepath), "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return {
            "media_id": generate_id("MED-"),
            "entity_type": "Employee",
            "entity_id": emp_id,
            "media_type": "Image",
            "media_sub_type": "Officer Profile",
            "file_name": filename,
            "storage_path": str(filepath),
            "thumbnail_path": str(thumb_path),
            "file_size_bytes": os.path.getsize(str(filepath)),
            "file_format": "jpg",
            "resolution": "200x250",
            "geotag_latitude": 0,
            "geotag_longitude": 0,
            "capture_datetime": datetime.now().isoformat(),
            "hash_md5": file_hash,
            "has_file": True,
        }

    # ──────────────────────────────────────────────────────
    # 3. Vehicle Images
    # ──────────────────────────────────────────────────────
    def _generate_vehicle_image(self, idx: int, dirs: dict) -> dict:
        """Generate a synthetic vehicle image with registration plate."""
        vehicle_types = ["Car", "Bike", "Auto", "Truck", "Bus", "SUV"]
        vtype = vehicle_types[idx % len(vehicle_types)]
        color_name = list(VEHICLE_COLORS_RGB.keys())[idx % len(VEHICLE_COLORS_RGB)]
        color_rgb = VEHICLE_COLORS_RGB[color_name]

        img = Image.new("RGB", (300, 200), color=(180, 190, 200))
        draw = ImageDraw.Draw(img)

        # Road
        draw.rectangle([0, 150, 300, 200], fill=(80, 80, 85))
        draw.line([(0, 175), (300, 175)], fill=(220, 200, 50), width=2)

        if vtype == "Car" or vtype == "SUV":
            # Car body
            draw.rounded_rectangle([60, 80, 240, 150], radius=10, fill=color_rgb)
            # Roof
            draw.rounded_rectangle([90, 50, 210, 90], radius=8, fill=(color_rgb[0] - 10, color_rgb[1] - 10, color_rgb[2] - 10))
            # Windows
            draw.rectangle([95, 55, 145, 85], fill=(150, 200, 240))
            draw.rectangle([155, 55, 205, 85], fill=(150, 200, 240))
            # Wheels
            draw.ellipse([75, 135, 110, 170], fill=(30, 30, 30))
            draw.ellipse([80, 140, 105, 165], fill=(60, 60, 60))
            draw.ellipse([190, 135, 225, 170], fill=(30, 30, 30))
            draw.ellipse([195, 140, 220, 165], fill=(60, 60, 60))
            # Headlights
            draw.ellipse([230, 100, 245, 115], fill=(255, 255, 200))
            draw.ellipse([55, 100, 70, 115], fill=(255, 100, 100))
        elif vtype == "Bike":
            # Bike body
            draw.ellipse([100, 120, 145, 165], fill=(30, 30, 30))  # Front wheel
            draw.ellipse([180, 120, 225, 165], fill=(30, 30, 30))  # Rear wheel
            draw.line([(123, 130), (200, 100)], fill=color_rgb, width=4)  # Frame
            draw.line([(200, 100), (203, 130)], fill=color_rgb, width=4)
            draw.rectangle([185, 85, 215, 105], fill=color_rgb)  # Tank
            draw.rectangle([155, 80, 185, 90], fill=(40, 40, 40))  # Seat
        elif vtype == "Auto":
            # Auto rickshaw
            draw.rounded_rectangle([80, 70, 220, 150], radius=15, fill=(50, 150, 50))
            draw.rectangle([85, 80, 140, 130], fill=(150, 200, 240))  # Windshield
            draw.ellipse([95, 135, 130, 170], fill=(30, 30, 30))  # Front wheel
            draw.ellipse([185, 135, 220, 170], fill=(30, 30, 30))  # Rear wheel
        elif vtype == "Truck":
            draw.rectangle([50, 60, 130, 150], fill=color_rgb)  # Cabin
            draw.rectangle([130, 80, 260, 150], fill=(color_rgb[0] - 30, color_rgb[1] - 30, color_rgb[2] - 30))
            draw.rectangle([55, 70, 120, 120], fill=(150, 200, 240))
            draw.ellipse([65, 135, 100, 170], fill=(30, 30, 30))
            draw.ellipse([220, 135, 255, 170], fill=(30, 30, 30))
        else:  # Bus
            draw.rounded_rectangle([30, 60, 270, 150], radius=8, fill=color_rgb)
            for wx in range(45, 260, 40):
                draw.rectangle([wx, 70, wx + 25, 110], fill=(150, 200, 240))
            draw.ellipse([50, 135, 85, 170], fill=(30, 30, 30))
            draw.ellipse([215, 135, 250, 170], fill=(30, 30, 30))

        # Registration plate
        plate_text = f"KA-{self.rng.integers(1,72):02d}-{chr(int(self.rng.integers(65,91)))}{chr(int(self.rng.integers(65,91)))}-{self.rng.integers(1000,9999)}"
        draw.rectangle([110, 152, 200, 168], fill="white", outline="black")
        try:
            font = ImageFont.truetype("arial.ttf", 10)
        except (OSError, IOError):
            font = ImageFont.load_default()
        draw.text((115, 153), plate_text, fill="black", font=font)

        vid = generate_id("VEH-")
        filename = f"vehicle_{idx:04d}_{vtype.lower()}.jpg"
        filepath = dirs["vehicles"] / filename
        img.save(str(filepath), "JPEG", quality=85)

        with open(str(filepath), "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return {
            "media_id": generate_id("MED-"),
            "entity_type": "Vehicle",
            "entity_id": vid,
            "media_type": "Image",
            "media_sub_type": f"{vtype} Photo",
            "file_name": filename,
            "storage_path": str(filepath),
            "thumbnail_path": "",
            "file_size_bytes": os.path.getsize(str(filepath)),
            "file_format": "jpg",
            "resolution": "300x200",
            "geotag_latitude": 0,
            "geotag_longitude": 0,
            "capture_datetime": datetime.now().isoformat(),
            "hash_md5": file_hash,
            "has_file": True,
        }

    # ──────────────────────────────────────────────────────
    # 4. Evidence Images
    # ──────────────────────────────────────────────────────
    def _generate_evidence_image(self, etype: str, econfig: dict, dirs: dict) -> dict:
        """Generate a synthetic evidence photo with evidence tag."""
        img = Image.new("RGB", (300, 300), color=econfig["bg"])
        draw = ImageDraw.Draw(img)

        # Evidence surface (table/ground)
        draw.rectangle([20, 200, 280, 290], fill=(80, 80, 85))

        # Scale ruler at bottom
        draw.rectangle([30, 270, 270, 280], fill="white")
        for tick in range(30, 270, 24):
            draw.line([(tick, 270), (tick, 280)], fill="black", width=1)

        # Draw evidence item
        label_color = econfig["label_color"]
        shape = econfig["shape"]
        if shape == "blade":
            draw.polygon([(150, 80), (130, 200), (140, 210), (160, 210), (170, 200)], fill=(160, 160, 170))
            draw.rectangle([140, 210, 160, 260], fill=(100, 60, 30))
        elif shape == "gun":
            draw.rectangle([80, 130, 220, 155], fill=(50, 50, 55))
            draw.rectangle([90, 155, 120, 200], fill=(50, 50, 55))
            draw.rectangle([190, 125, 230, 140], fill=(50, 50, 55))
        elif shape == "rect":  # Mobile
            draw.rounded_rectangle([110, 80, 190, 220], radius=8, fill=(20, 20, 25))
            draw.rectangle([115, 90, 185, 200], fill=(40, 60, 80))
        elif shape == "rect_wide":  # Laptop
            draw.rectangle([60, 100, 240, 195], fill=(30, 30, 35))
            draw.rectangle([65, 105, 235, 190], fill=(50, 70, 90))
            draw.rectangle([50, 195, 250, 210], fill=(40, 40, 45))
        elif shape == "bundle":  # Cash
            for b in range(5):
                y_off = b * 8
                draw.rectangle([100, 120 + y_off, 200, 150 + y_off], fill=(80, 140, 80))
                draw.rectangle([105, 125 + y_off, 195, 145 + y_off], fill=(60, 120, 60))
        elif shape == "packet":  # Drug
            draw.rounded_rectangle([100, 100, 200, 200], radius=5, fill=(200, 200, 180))
            draw.text((120, 140), "SEIZED", fill=(200, 50, 50))
        elif shape == "paper":  # Document
            draw.rectangle([90, 70, 210, 230], fill=(250, 245, 235))
            for line_y in range(85, 220, 12):
                draw.line([(100, line_y), (200, line_y)], fill=(180, 180, 180), width=1)

        # Evidence tag
        draw.rectangle([10, 10, 120, 40], fill=(255, 255, 100))
        draw.rectangle([10, 10, 120, 40], outline="red", width=2)
        try:
            font = ImageFont.truetype("arial.ttf", 11)
        except (OSError, IOError):
            font = ImageFont.load_default()
        draw.text((15, 15), f"EVIDENCE: {etype}", fill="red", font=font)

        # Case number tag
        case_num = f"CR/{self.rng.integers(2020,2027)}/{self.rng.integers(1,9999):04d}"
        draw.rectangle([10, 45, 150, 65], fill=(255, 255, 255))
        draw.text((15, 48), f"Case: {case_num}", fill="black", font=font)

        evd_id = generate_id("EVD-")
        filename = f"evidence_{etype.lower().replace(' ', '_')}.jpg"
        filepath = dirs["evidence"] / filename
        img.save(str(filepath), "JPEG", quality=90)

        with open(str(filepath), "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return {
            "media_id": generate_id("MED-"),
            "entity_type": "Evidence",
            "entity_id": evd_id,
            "media_type": "Image",
            "media_sub_type": f"Evidence - {etype}",
            "file_name": filename,
            "storage_path": str(filepath),
            "thumbnail_path": "",
            "file_size_bytes": os.path.getsize(str(filepath)),
            "file_format": "jpg",
            "resolution": "300x300",
            "geotag_latitude": 0,
            "geotag_longitude": 0,
            "capture_datetime": datetime.now().isoformat(),
            "hash_md5": file_hash,
            "has_file": True,
        }

    # ──────────────────────────────────────────────────────
    # 5. Crime Scene Images
    # ──────────────────────────────────────────────────────
    def _generate_crime_scene_image(self, idx: int, dirs: dict) -> dict:
        """Generate a synthetic crime scene overview image."""
        scene_types = ["Burglary", "Accident", "Assault", "Theft", "Vandalism",
                       "Drug Seizure", "Weapon Recovery", "Vehicle Theft", "Fraud", "Arson"]
        scene_type = scene_types[idx % len(scene_types)]

        img = Image.new("RGB", (400, 300), color=(60, 65, 70))
        draw = ImageDraw.Draw(img)

        # Ground/floor
        draw.rectangle([0, 200, 400, 300], fill=(100, 95, 85))

        # Crime scene tape
        for x_start in range(0, 400, 80):
            draw.rectangle([x_start, 10, x_start + 40, 30], fill=(255, 200, 0))
            draw.rectangle([x_start + 40, 10, x_start + 80, 30], fill=(20, 20, 20))

        # Evidence markers (numbered cones)
        for m in range(1, int(self.rng.integers(3, 7))):
            mx = int(self.rng.integers(50, 350))
            my = int(self.rng.integers(180, 280))
            draw.polygon([(mx, my - 20), (mx - 8, my), (mx + 8, my)], fill=(255, 200, 0))
            try:
                font = ImageFont.truetype("arial.ttf", 10)
            except (OSError, IOError):
                font = ImageFont.load_default()
            draw.text((mx - 3, my - 16), str(m), fill="black", font=font)

        # Scene label
        draw.rectangle([10, 35, 200, 60], fill=(0, 0, 0, 180))
        try:
            font_large = ImageFont.truetype("arial.ttf", 14)
        except (OSError, IOError):
            font_large = ImageFont.load_default()
        draw.text((15, 38), f"CRIME SCENE: {scene_type}", fill="white", font=font_large)

        # Timestamp
        ts = f"{self.rng.integers(2020,2027)}-{self.rng.integers(1,13):02d}-{self.rng.integers(1,29):02d} {self.rng.integers(0,24):02d}:{self.rng.integers(0,60):02d}"
        draw.text((15, 280), f"Captured: {ts}", fill="yellow", font=font)

        # GPS coordinates
        lat = round(12.5 + float(self.rng.uniform(0, 5)), 4)
        lon = round(74.5 + float(self.rng.uniform(0, 4)), 4)
        draw.text((250, 280), f"GPS: {lat}, {lon}", fill="yellow", font=font)

        filename = f"crime_scene_{idx:04d}_{scene_type.lower().replace(' ', '_')}.jpg"
        filepath = dirs["crime_scenes"] / filename
        img.save(str(filepath), "JPEG", quality=90)

        with open(str(filepath), "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return {
            "media_id": generate_id("MED-"),
            "entity_type": "CrimeScene",
            "entity_id": generate_id("CASE-"),
            "media_type": "Image",
            "media_sub_type": f"Crime Scene - {scene_type}",
            "file_name": filename,
            "storage_path": str(filepath),
            "thumbnail_path": "",
            "file_size_bytes": os.path.getsize(str(filepath)),
            "file_format": "jpg",
            "resolution": "400x300",
            "geotag_latitude": lat,
            "geotag_longitude": lon,
            "capture_datetime": ts,
            "hash_md5": file_hash,
            "has_file": True,
        }

    # ──────────────────────────────────────────────────────
    # 6. CCTV Frames
    # ──────────────────────────────────────────────────────
    def _generate_cctv_frame(self, idx: int, dirs: dict) -> dict:
        """Generate a synthetic CCTV camera frame with timestamp overlay."""
        img = Image.new("RGB", (640, 480), color=(25, 30, 35))
        draw = ImageDraw.Draw(img)

        # Simulate low-light CCTV look
        # Road
        draw.rectangle([0, 350, 640, 480], fill=(50, 50, 55))
        draw.line([(0, 400), (640, 400)], fill=(70, 65, 45), width=2)

        # Buildings/walls
        draw.rectangle([0, 100, 150, 350], fill=(45, 45, 50))
        draw.rectangle([500, 80, 640, 350], fill=(40, 42, 48))

        # Windows (lit)
        for wy in range(120, 330, 50):
            for wx in [20, 70, 120, 520, 570]:
                if self.rng.random() < 0.4:
                    draw.rectangle([wx, wy, wx + 30, wy + 25], fill=(80, 75, 50))

        # Street light
        draw.rectangle([320, 50, 325, 350], fill=(60, 60, 65))
        draw.ellipse([305, 40, 340, 60], fill=(200, 190, 140))
        # Light cone
        draw.polygon([(310, 60), (250, 350), (390, 350), (335, 60)],
                     fill=(40, 38, 30))

        # Person silhouettes
        n_persons = int(self.rng.integers(0, 5))
        for p in range(n_persons):
            px = int(self.rng.integers(160, 490))
            py = int(self.rng.integers(280, 340))
            # Head
            draw.ellipse([px - 5, py - 30, px + 5, py - 18], fill=(50, 50, 55))
            # Body
            draw.rectangle([px - 7, py - 18, px + 7, py + 10], fill=(45, 48, 52))
            # Legs
            draw.line([(px - 3, py + 10), (px - 5, py + 30)], fill=(40, 40, 45), width=2)
            draw.line([(px + 3, py + 10), (px + 5, py + 30)], fill=(40, 40, 45), width=2)

        # Vehicle
        if self.rng.random() < 0.6:
            vx = int(self.rng.integers(200, 500))
            draw.rectangle([vx, 360, vx + 80, 395], fill=(55, 55, 60))
            draw.ellipse([vx + 5, 385, vx + 25, 405], fill=(30, 30, 33))
            draw.ellipse([vx + 55, 385, vx + 75, 405], fill=(30, 30, 33))
            # Headlights
            draw.ellipse([vx + 75, 370, vx + 85, 380], fill=(180, 170, 120))

        # CCTV overlay
        cam_id = f"CAM-{self.rng.integers(1,500):04d}"
        ts = f"{self.rng.integers(2020,2027)}-{self.rng.integers(1,13):02d}-{self.rng.integers(1,29):02d} {self.rng.integers(0,24):02d}:{self.rng.integers(0,60):02d}:{self.rng.integers(0,60):02d}"
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except (OSError, IOError):
            font = ImageFont.load_default()

        # Top bar
        draw.rectangle([0, 0, 640, 25], fill=(0, 0, 0))
        draw.text((10, 5), f"{cam_id} | {ts}", fill=(200, 200, 200), font=font)
        draw.text((500, 5), "● REC", fill=(255, 50, 50), font=font)

        # Bottom status
        draw.rectangle([0, 455, 640, 480], fill=(0, 0, 0))
        lat = round(12.5 + float(self.rng.uniform(0, 5)), 4)
        lon = round(74.5 + float(self.rng.uniform(0, 4)), 4)
        draw.text((10, 460), f"GPS: {lat}, {lon} | Persons: {n_persons}", fill=(150, 150, 150), font=font)

        # Noise effect
        noise = np.random.randint(0, 15, (480, 640, 3), dtype=np.uint8)
        noise_img = Image.fromarray(noise)
        img = Image.blend(img, noise_img, 0.05)

        filename = f"cctv_frame_{idx:04d}.jpg"
        filepath = dirs["cctv_frames"] / filename
        img.save(str(filepath), "JPEG", quality=75)

        with open(str(filepath), "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return {
            "media_id": generate_id("MED-"),
            "entity_type": "CCTV",
            "entity_id": cam_id,
            "media_type": "Image",
            "media_sub_type": "CCTV Frame",
            "file_name": filename,
            "storage_path": str(filepath),
            "thumbnail_path": "",
            "file_size_bytes": os.path.getsize(str(filepath)),
            "file_format": "jpg",
            "resolution": "640x480",
            "geotag_latitude": lat,
            "geotag_longitude": lon,
            "capture_datetime": ts,
            "hash_md5": file_hash,
            "has_file": True,
        }

    # ──────────────────────────────────────────────────────
    # 7. Fingerprint Images
    # ──────────────────────────────────────────────────────
    def _generate_fingerprint_image(self, idx: int, dirs: dict) -> dict:
        """Generate a synthetic fingerprint image with ridge patterns."""
        img = Image.new("L", (200, 250), color=240)  # Grayscale
        draw = ImageDraw.Draw(img)

        cx, cy = 100, 125

        # Generate concentric ridge patterns
        n_ridges = int(self.rng.integers(15, 30))
        pattern_type = int(self.rng.integers(0, 3))  # 0=loop, 1=whorl, 2=arch

        for r in range(3, n_ridges * 4, 4):
            angle_offset = float(self.rng.uniform(0, 0.5))
            points = []
            for theta in range(0, 360, 5):
                rad = math.radians(theta + angle_offset * r)
                if pattern_type == 0:  # Loop
                    rx = r * (1.0 + 0.3 * math.sin(rad * 2))
                    ry = r * (1.0 + 0.2 * math.cos(rad))
                elif pattern_type == 1:  # Whorl
                    rx = r * (1.0 + 0.15 * math.sin(rad * 3 + r * 0.1))
                    ry = r * (1.0 + 0.15 * math.cos(rad * 3 + r * 0.1))
                else:  # Arch
                    rx = r * (1.0 + 0.4 * math.sin(rad))
                    ry = r * 0.7

                x = cx + int(rx * math.cos(rad))
                y = cy + int(ry * math.sin(rad))
                points.append((x, y))

            if len(points) > 2:
                gray_val = max(0, 240 - int(self.rng.integers(60, 120)))
                draw.line(points, fill=gray_val, width=1)

        # Add some minutiae points (ridge endings/bifurcations)
        for _ in range(int(self.rng.integers(8, 20))):
            mx = cx + int(self.rng.integers(-60, 60))
            my = cy + int(self.rng.integers(-80, 80))
            draw.ellipse([mx - 2, my - 2, mx + 2, my + 2], fill=100)

        # Border
        draw.rectangle([0, 0, 199, 249], outline=0, width=2)

        # Label
        try:
            font = ImageFont.truetype("arial.ttf", 10)
        except (OSError, IOError):
            font = ImageFont.load_default()
        fp_id = f"FP-{self.rng.integers(10000, 99999)}"
        draw.text((10, 235), fp_id, fill=0, font=font)
        types_label = ["Loop", "Whorl", "Arch"][pattern_type]
        draw.text((130, 235), types_label, fill=0, font=font)

        # Convert to RGB for saving
        img_rgb = img.convert("RGB")

        filename = f"fingerprint_{idx:04d}.jpg"
        filepath = dirs["fingerprints"] / filename
        img_rgb.save(str(filepath), "JPEG", quality=90)

        with open(str(filepath), "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return {
            "media_id": generate_id("MED-"),
            "entity_type": "Forensic",
            "entity_id": fp_id,
            "media_type": "Image",
            "media_sub_type": f"Fingerprint - {types_label}",
            "file_name": filename,
            "storage_path": str(filepath),
            "thumbnail_path": "",
            "file_size_bytes": os.path.getsize(str(filepath)),
            "file_format": "jpg",
            "resolution": "200x250",
            "geotag_latitude": 0,
            "geotag_longitude": 0,
            "capture_datetime": datetime.now().isoformat(),
            "hash_md5": file_hash,
            "has_file": True,
        }

    # ──────────────────────────────────────────────────────
    # 8. Signature Images
    # ──────────────────────────────────────────────────────
    def _generate_signature_image(self, idx: int, dirs: dict) -> dict:
        """Generate a synthetic signature image using random bezier-like strokes."""
        img = Image.new("RGB", (300, 100), color=(255, 255, 250))
        draw = ImageDraw.Draw(img)

        ink_color = (10, 10, 60)
        n_strokes = int(self.rng.integers(3, 8))
        x_cursor = int(self.rng.integers(20, 60))

        for s in range(n_strokes):
            points = []
            n_points = int(self.rng.integers(5, 15))
            y_base = int(self.rng.integers(30, 70))

            for p in range(n_points):
                x = x_cursor + p * int(self.rng.integers(3, 12))
                y = y_base + int(self.rng.normal(0, 8))
                points.append((x, y))

            if len(points) >= 2:
                draw.line(points, fill=ink_color, width=int(self.rng.integers(1, 3)))

            x_cursor = points[-1][0] + int(self.rng.integers(-5, 15))

        # Underline flourish
        draw.line([(30, 80), (x_cursor + 20, 80)], fill=ink_color, width=1)

        sig_id = generate_id("SIG-")
        filename = f"signature_{idx:04d}.png"
        filepath = dirs["signatures"] / filename
        img.save(str(filepath), "PNG")

        with open(str(filepath), "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return {
            "media_id": generate_id("MED-"),
            "entity_type": "Signature",
            "entity_id": sig_id,
            "media_type": "Image",
            "media_sub_type": "Signature",
            "file_name": filename,
            "storage_path": str(filepath),
            "thumbnail_path": "",
            "file_size_bytes": os.path.getsize(str(filepath)),
            "file_format": "png",
            "resolution": "300x100",
            "geotag_latitude": 0,
            "geotag_longitude": 0,
            "capture_datetime": datetime.now().isoformat(),
            "hash_md5": file_hash,
            "has_file": True,
        }

    # ──────────────────────────────────────────────────────
    # 9. Crime Heatmaps
    # ──────────────────────────────────────────────────────
    def _generate_heatmap(self, district: pd.Series, dirs: dict) -> dict:
        """Generate a synthetic crime density heatmap for a district."""
        img = Image.new("RGB", (400, 400), color=(20, 25, 30))
        draw = ImageDraw.Draw(img)

        dist_name = district["district_name"]

        # Generate random hotspot blobs
        heatmap = np.zeros((400, 400, 3), dtype=np.float64)
        n_hotspots = int(self.rng.integers(3, 10))

        for _ in range(n_hotspots):
            hx = int(self.rng.integers(50, 350))
            hy = int(self.rng.integers(50, 350))
            intensity = float(self.rng.uniform(0.3, 1.0))
            radius = int(self.rng.integers(30, 80))

            for y in range(max(0, hy - radius), min(400, hy + radius)):
                for x in range(max(0, hx - radius), min(400, hx + radius)):
                    dist_sq = (x - hx) ** 2 + (y - hy) ** 2
                    if dist_sq < radius ** 2:
                        falloff = 1.0 - (dist_sq / (radius ** 2))
                        val = intensity * falloff
                        # Red-yellow-green gradient
                        if val > 0.7:
                            heatmap[y, x] = [min(255, heatmap[y, x, 0] + val * 255), min(80, heatmap[y, x, 1] + val * 30), 0]
                        elif val > 0.3:
                            heatmap[y, x] = [min(255, heatmap[y, x, 0] + val * 200), min(200, heatmap[y, x, 1] + val * 180), 0]
                        else:
                            heatmap[y, x] = [0, min(200, heatmap[y, x, 1] + val * 150), min(100, heatmap[y, x, 2] + val * 80)]

        heatmap_img = Image.fromarray(heatmap.astype(np.uint8))
        img = Image.blend(img, heatmap_img, 0.8)
        draw = ImageDraw.Draw(img)

        # Title
        try:
            font = ImageFont.truetype("arial.ttf", 16)
            font_small = ImageFont.truetype("arial.ttf", 11)
        except (OSError, IOError):
            font = ImageFont.load_default()
            font_small = font

        draw.rectangle([0, 0, 400, 30], fill=(0, 0, 0, 200))
        draw.text((10, 5), f"Crime Density: {dist_name}", fill="white", font=font)

        # Legend
        draw.rectangle([320, 350, 390, 395], fill=(0, 0, 0, 180))
        draw.rectangle([325, 355, 340, 365], fill=(255, 50, 0))
        draw.text((345, 355), "High", fill="white", font=font_small)
        draw.rectangle([325, 370, 340, 380], fill=(255, 200, 0))
        draw.text((345, 370), "Medium", fill="white", font=font_small)
        draw.rectangle([325, 385, 340, 395], fill=(0, 150, 80))
        draw.text((345, 385), "Low", fill="white", font=font_small)

        filename = f"heatmap_{dist_name.lower().replace(' ', '_')}.jpg"
        filepath = dirs["maps"] / filename
        img.save(str(filepath), "JPEG", quality=90)

        with open(str(filepath), "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return {
            "media_id": generate_id("MED-"),
            "entity_type": "Map",
            "entity_id": district["district_id"],
            "media_type": "Image",
            "media_sub_type": "Crime Heatmap",
            "file_name": filename,
            "storage_path": str(filepath),
            "thumbnail_path": "",
            "file_size_bytes": os.path.getsize(str(filepath)),
            "file_format": "jpg",
            "resolution": "400x400",
            "geotag_latitude": float(district.get("latitude", 0)),
            "geotag_longitude": float(district.get("longitude", 0)),
            "capture_datetime": datetime.now().isoformat(),
            "hash_md5": file_hash,
            "has_file": True,
        }

    # ──────────────────────────────────────────────────────
    # 10. PDF Documents (FIR)
    # ──────────────────────────────────────────────────────
    def _generate_fir_pdf(self, idx: int, persons: pd.DataFrame, dirs: dict) -> Optional[dict]:
        """Generate a synthetic FIR PDF document."""
        if not HAS_REPORTLAB:
            return None

        fir_id = generate_id("FIR-")
        filename = f"FIR_{idx:04d}_{fir_id}.pdf"
        filepath = dirs["documents"] / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                                topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                                leftMargin=2 * cm, rightMargin=2 * cm)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("FIRTitle", parent=styles["Title"],
                                     fontSize=16, alignment=TA_CENTER, spaceAfter=6)
        header_style = ParagraphStyle("FIRHeader", parent=styles["Heading2"],
                                      fontSize=12, spaceAfter=4, spaceBefore=8)
        body_style = ParagraphStyle("FIRBody", parent=styles["Normal"],
                                    fontSize=10, alignment=TA_JUSTIFY, spaceAfter=4)

        elements = []

        # Header
        elements.append(Paragraph("KARNATAKA STATE POLICE", title_style))
        elements.append(Paragraph("FIRST INFORMATION REPORT", title_style))
        elements.append(Spacer(1, 0.3 * cm))

        # FIR Details table
        crime_num = f"{self.rng.integers(2020,2027)}/{self.rng.integers(1,9999):04d}"
        station = f"PS-{self.rng.integers(1,500):04d}"
        district_names = ["Bengaluru Urban", "Mysuru", "Belagavi", "Mangaluru", "Dharwad"]
        district = district_names[idx % len(district_names)]

        fir_data = [
            ["FIR Number", crime_num, "District", district],
            ["Police Station", station, "Year", str(self.rng.integers(2020, 2027))],
            ["Date of Report", f"{self.rng.integers(1,29):02d}/{self.rng.integers(1,13):02d}/{self.rng.integers(2020,2027)}", "Time", f"{self.rng.integers(0,24):02d}:{self.rng.integers(0,60):02d}"],
        ]

        fir_table = Table(fir_data, colWidths=[3.5 * cm, 5 * cm, 3.5 * cm, 5 * cm])
        fir_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("BACKGROUND", (2, 0), (2, -1), colors.lightgrey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(fir_table)
        elements.append(Spacer(1, 0.5 * cm))

        # Complainant
        elements.append(Paragraph("1. COMPLAINANT DETAILS", header_style))
        if not persons.empty:
            p = persons.iloc[idx % len(persons)]
            comp_text = (
                f"Name: {p.get('full_name', 'N/A')}<br/>"
                f"Age: {p.get('age', 'N/A')} | Gender: {p.get('gender', 'N/A')}<br/>"
                f"Address: {p.get('address', 'N/A')}, {p.get('district', 'N/A')}<br/>"
                f"Phone: {p.get('phone_primary', 'N/A')}"
            )
        else:
            comp_text = "Name: N/A"
        elements.append(Paragraph(comp_text, body_style))
        elements.append(Spacer(1, 0.3 * cm))

        # Incident Details
        elements.append(Paragraph("2. INCIDENT DETAILS", header_style))
        crime_types = ["Theft", "Robbery", "Assault", "Cyber Fraud", "Burglary"]
        incident_text = (
            f"Type of Offence: {crime_types[idx % len(crime_types)]}<br/>"
            f"Date of Incident: {self.rng.integers(1,29):02d}/{self.rng.integers(1,13):02d}/{self.rng.integers(2020,2027)}<br/>"
            f"Time of Incident: {self.rng.integers(0,24):02d}:{self.rng.integers(0,60):02d}<br/>"
            f"Place of Incident: Ward {self.rng.integers(1,50)}, {district}<br/>"
        )
        elements.append(Paragraph(incident_text, body_style))
        elements.append(Spacer(1, 0.3 * cm))

        # Brief Facts
        elements.append(Paragraph("3. BRIEF FACTS", header_style))
        facts = (
            "The complainant states that on the above-mentioned date and time, "
            "while going about their daily routine, the incident occurred at the "
            "location mentioned above. The complainant immediately approached the "
            "nearest police station to file this report. Based on the complaint, "
            "a case has been registered and investigation is underway."
        )
        elements.append(Paragraph(facts, body_style))
        elements.append(Spacer(1, 0.5 * cm))

        # Signature
        elements.append(Paragraph("Signature of the Complainant: _______________", body_style))
        elements.append(Spacer(1, 0.3 * cm))
        elements.append(Paragraph("Signature of the SHO: _______________", body_style))
        elements.append(Spacer(1, 0.3 * cm))
        elements.append(Paragraph(f"<i>Generated by Crime Simulation Laboratory v{self.config.version}</i>", body_style))

        doc.build(elements)

        with open(str(filepath), "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return {
            "media_id": generate_id("MED-"),
            "entity_type": "Document",
            "entity_id": fir_id,
            "media_type": "Document",
            "media_sub_type": "FIR",
            "file_name": filename,
            "storage_path": str(filepath),
            "thumbnail_path": "",
            "file_size_bytes": os.path.getsize(str(filepath)),
            "file_format": "pdf",
            "resolution": "A4",
            "geotag_latitude": 0,
            "geotag_longitude": 0,
            "capture_datetime": datetime.now().isoformat(),
            "hash_md5": file_hash,
            "has_file": True,
        }

    # ──────────────────────────────────────────────────────
    # Metadata-only records for all entities
    # ──────────────────────────────────────────────────────
    def _generate_metadata_only_records(
        self, persons: pd.DataFrame, employees: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate metadata-only records for entities that don't have actual image files.
        In production mode, these can be filled in by a batch image generation worker.
        """
        records = []

        # For persons without images
        existing_ids = set()  # Would be populated from media_assets
        for _, person in persons.iterrows():
            pid = person["person_id"]
            if pid not in existing_ids:
                records.append({
                    "media_id": generate_id("MED-"),
                    "entity_type": "Person",
                    "entity_id": pid,
                    "media_type": "Image",
                    "media_sub_type": "Profile Photo",
                    "file_name": f"{pid}.jpg",
                    "storage_path": f"media/images/persons/{pid}.jpg",
                    "thumbnail_path": f"media/thumbnails/thumb_{pid}.jpg",
                    "file_size_bytes": 0,
                    "file_format": "jpg",
                    "resolution": "200x250",
                    "geotag_latitude": float(person.get("latitude", 0)),
                    "geotag_longitude": float(person.get("longitude", 0)),
                    "capture_datetime": "",
                    "hash_md5": "",
                    "has_file": False,  # Flag: no actual file generated
                })

        return pd.DataFrame(records) if records else pd.DataFrame()

    # ──────────────────────────────────────────────────────
    # Utility
    # ──────────────────────────────────────────────────────
    def _draw_star(self, draw, cx, cy, size, color):
        """Draw a small star shape."""
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = size if i % 2 == 0 else size / 2
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        draw.polygon(points, fill=color)
