"""
Take a folder with mdl files and make a simobject folder
Need to add textures manually
Reccomended to generate an html report with ModelConverterX to list needed textures
"""
import glob
import os.path
import shutil
import sys

boat_cfg = """
[General]
category=Boat

[contact_points]
static_pitch=0.0                //degrees, pitch when at rest on the ground (+=Up, -=Dn)
static_cg_height=0.0             //feet, altitude of CG when at rest on the ground

[DesignSpecs]
max_speed_mph = 40     
acceleration_constants = 0.5, 0.4               //Time constant (effects responsiveness), and max acceleration (Gs)
deceleration_constants = 2.0, 0.5               //Time constant (effects responsiveness), and max acceleration (Gs)
SternPosition = 1

[Effects]
wake = fx_wake_s
"""

veh_cfg = """
[General]
category=GroundVehicle

[contact_points]
wheel_radius=2.03

static_pitch=0.0                //degrees, pitch when at rest on the ground (+=Up, -=Dn)
static_cg_height=2.27            //feet, altitude of CG when at rest on the ground

[DesignSpecs]
max_speed_mph = 30     
acceleration_constants = 0.3, 0.4     //Time constant (effects responsiveness), and max G acceleration
deceleration_constants = 0.2, 0.4     //Time constant (effects responsiveness), and max G acceleratione
"""

misc_cfg = """
[General]
category=SimpleObject

[contact_points]
destroy_on_impact=0
"""


def main():
    try:
        prefix = sys.argv[1]
    except Exception:
        print(f"Usage: {sys.argv[0]} <output_folder>")
        sys.exit(1)
    for folder in next(os.walk(prefix))[1]:
        models_entries = []
        folder = os.path.join(prefix, folder)
        print(folder)
        obj_type = input("type:\n1) Boat\n2) GroundVehicle\n3) Misc").strip()
        out_dir = os.path.join(prefix, folder, "output")
        try:
            os.mkdir(out_dir)
        except FileExistsError:
            pass
        texture_dir = os.path.join(out_dir, "texture")
        for i, mdl_file_path in enumerate(glob.glob(os.path.join(folder, "*.mdl"), recursive=True)):
            _, mdl_file_name = os.path.split(mdl_file_path)
            mdl_name, _ = os.path.splitext(mdl_file_name)
            model_dir = os.path.join(out_dir, f"model.{mdl_name}")
            try:
                os.mkdir(model_dir)
            except FileExistsError:
                pass

            with open(os.path.join(model_dir, "model.cfg"), "w") as outfile:
                model_cfg_string = f"[models]\nnormal={mdl_name}"
                outfile.write(model_cfg_string)
            shutil.copy(mdl_file_path, os.path.join(model_dir, mdl_file_name))
            models_entries.append(f"""[fltsim.{i}]
title={mdl_name}
model={mdl_name}
texture=
""")
        # end inner loop
        with open(os.path.join(out_dir, "sim.cfg"), "w") as outfile:
            outfile.write("\n".join(models_entries))
            obj_type_string = {
                "1": boat_cfg,
                "2": veh_cfg,
                "3": misc_cfg
            }[obj_type]
            outfile.write(obj_type_string)

        if os.path.isdir(os.path.join(folder, "texture")):
            shutil.copytree(os.path.join(folder, "texture"), texture_dir)
        else:
            try:
                os.mkdir(texture_dir)
            except FileExistsError:
                pass


if __name__ == '__main__':
    main()
