#!/usr/bin/env python3
import os

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

STATIONS = {
    "qr_home": "HOME_BASE",
    "qr_shelf_a": "SHELF_A",
    "qr_shelf_b": "SHELF_B",
    "qr_pickup": "PICKUP_ZONE",
    "qr_dropoff": "DROPOFF_ZONE"
}

MODEL_CONFIG = """<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author>
    <name>Auto Generated</name>
    <email>auto@generated</email>
  </author>
  <description>QR Code Board for {model_name}</description>
</model>
"""

MODEL_SDF_TEMPLATE = """<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{model_name}">
    <static>true</static>
    <link name="link">
      <visual name="board_visual">
        <pose>0 0 0 0 0 0</pose>
        <geometry>
          <box>
            <size>0.01 0.50 0.50</size>
          </box>
        </geometry>
        <material>
          <script>
            <uri>model://{model_name}/materials/scripts</uri>
            <uri>model://{model_name}/materials/textures</uri>
            <name>QRBoard/{model_name}</name>
          </script>
        </material>
      </visual>
    </link>
  </model>
</sdf>
"""

MATERIAL = """material QRBoard/{model_name}
{{
  technique
  {{
    pass
    {{
      ambient 1.0 1.0 1.0 1.0
      diffuse 1.0 1.0 1.0 1.0
      emissive 0.8 0.8 0.8 1.0
      texture_unit
      {{
        texture {model_name}.png
        filtering anisotropic
        max_anisotropy 16
      }}
    }}
  }}
}}
"""

def generate():
    for model_name, qr_data in STATIONS.items():
        base_dir = os.path.join(MODELS_DIR, model_name)
        mat_scripts_dir = os.path.join(base_dir, "materials", "scripts")
        mat_textures_dir = os.path.join(base_dir, "materials", "textures")

        os.makedirs(mat_scripts_dir, exist_ok=True)
        os.makedirs(mat_textures_dir, exist_ok=True)

        with open(os.path.join(base_dir, "model.config"), "w") as f:
            f.write(MODEL_CONFIG.format(model_name=model_name))

        with open(os.path.join(base_dir, "model.sdf"), "w") as f:
            f.write(MODEL_SDF_TEMPLATE.format(model_name=model_name))

        with open(os.path.join(mat_scripts_dir, "qr.material"), "w") as f:
            f.write(MATERIAL.format(model_name=model_name))

        import urllib.request
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=512x512&data={qr_data}"
        urllib.request.urlretrieve(url, os.path.join(mat_textures_dir, f"{model_name}.png"))
        print(f"Downloaded {model_name} with data: {qr_data}")

if __name__ == "__main__":
    generate()
