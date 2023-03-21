from bpy.app.handlers import persistent
import bpy
import os
import shutil
import time
import tempfile
import base64
import requests

# specify your images output folder
IMAGE_FOLDER = "//sd_results"

# if you don't want to send your maps to AI, set this option to False
is_using_ai = True

# which maps are you going to send to AI
is_send_canny = False
is_send_depth = False
is_send_bone = True
is_send_seg = False


@persistent
def render_complete_handler(scene):
    is_img_ready = bpy.data.images["Render Result"].has_data

    if is_img_ready:
        if is_using_ai:
            send_to_api(scene)
    else:
        print("Rendered image is not ready.")


def send_to_api(scene):
    # prepare filenames
    # FIXME: if you found nothing in image folder, navigate to the first frame
    comp_output_canny_filename = "canny0000.png"
    comp_output_depth_filename = "depth0000.png"
    comp_output_bone_filename = "bone0000.png"
    comp_output_seg_filename = "seg0000.png"

    timestamp = int(time.time())
    before_output_canny_filename = f"{timestamp}-1-canny-before.png"
    before_output_depth_filename = f"{timestamp}-1-depth-before.png"
    before_output_bone_filename = f"{timestamp}-1-bone-before.png"
    before_output_seg_filename = f"{timestamp}-1-seg-before.png"
    after_output_filename_prefix = f"{timestamp}-2-after"

    # check if comp output images exists
    if is_send_canny:
        if not os.path.exists(get_asset_path(comp_output_canny_filename)):
            return print("Couldn't find the canny image.")
        else:
            os.rename(
                get_asset_path(comp_output_canny_filename),
                get_asset_path(before_output_canny_filename),
            )
    if is_send_depth:
        if not os.path.exists(get_asset_path(comp_output_depth_filename)):
            return print("Couldn't find the depth image.")
        else:
            os.rename(
                get_asset_path(comp_output_depth_filename),
                get_asset_path(before_output_depth_filename),
            )
    if is_send_bone:
        if not os.path.exists(get_asset_path(comp_output_bone_filename)):
            return print("Couldn't find the bone image.")
        else:
            os.rename(
                get_asset_path(comp_output_bone_filename),
                get_asset_path(before_output_bone_filename),
            )
    if is_send_seg:
        if not os.path.exists(get_asset_path(comp_output_seg_filename)):
            return print("Couldn't find the seg image.")
        else:
            os.rename(
                get_asset_path(comp_output_seg_filename),
                get_asset_path(before_output_seg_filename),
            )

    # prepare data for API
    params = {
        "prompt": "a room",
        "negative_prompt": "(worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality",
        "width": get_output_width(scene),
        "height": get_output_height(scene),
        "sampler_index": "DPM++ SDE Karras",
        "sampler_name": "",
        "batch_size": 1,
        "n_iter": 1,
        "steps": 20,
        "cfg_scale": 7,
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0,
        "restore_faces": False,
        "enable_hr": False,
        "hr_scale": 1.5,
        "hr_upscaler": "R-ESRGAN General WDN 4xV3",
        "denoising_strength": 0.5,
        "hr_second_pass_steps": 10,
        "hr_resize_x": 0,
        "hr_resize_y": 0,
        "firstphase_width": 0,
        "firstphase_height": 0,
        "override_settings": {"CLIP_stop_at_last_layers": 2},
        "override_settings_restore_afterwards": True,
        "alwayson_scripts": {"controlnet": {"args": []}},
    }

    # if is_send_canny is True:
    if is_send_canny:
        canny_cn_units = {
            "mask": "",
            "module": "none",
            "model": "diff_control_sd15_canny_fp16 [ea6e3b9c]",
            "weight": 1.2,
            "resize_mode": "Scale to Fit (Inner Fit)",
            "lowvram": False,
            "processor_res": 64,
            "threshold_a": 64,
            "threshold_b": 64,
            "guidance": 1,
            "guidance_start": 0.19,
            "guidance_end": 1,
            "guessmode": False,
        }
        with open(get_asset_path(before_output_canny_filename), "rb") as canny_file:
            canny_cn_units["input_image"] = base64.b64encode(canny_file.read()).decode()
        params["alwayson_scripts"]["controlnet"]["args"].append(canny_cn_units)

    # if is_send_depth is True:
    if is_send_depth:
        depth_cn_units = {
            "mask": "",
            "module": "none",
            "model": "diff_control_sd15_depth_fp16 [978ef0a1]",
            "weight": 1.2,
            "resize_mode": "Scale to Fit (Inner Fit)",
            "lowvram": False,
            "processor_res": 64,
            "threshold_a": 64,
            "threshold_b": 64,
            "guidance": 1,
            "guidance_start": 0.19,
            "guidance_end": 1,
            "guessmode": False,
        }
        with open(get_asset_path(before_output_depth_filename), "rb") as depth_file:
            depth_cn_units["input_image"] = base64.b64encode(depth_file.read()).decode()
        params["alwayson_scripts"]["controlnet"]["args"].append(depth_cn_units)

    # if is_send_bone is True:
    if is_send_bone:
        bone_cn_units = {
            "mask": "",
            "module": "none",
            "model": "diff_control_sd15_openpose_fp16 [1723948e]",
            "weight": 1.1,
            "resize_mode": "Scale to Fit (Inner Fit)",
            "lowvram": False,
            "processor_res": 64,
            "threshold_a": 64,
            "threshold_b": 64,
            "guidance": 1,
            "guidance_start": 0,
            "guidance_end": 1,
            "guessmode": False,
        }
        with open(get_asset_path(before_output_bone_filename), "rb") as bone_file:
            bone_cn_units["input_image"] = base64.b64encode(bone_file.read()).decode()
        params["alwayson_scripts"]["controlnet"]["args"].append(bone_cn_units)

    # if is_send_seg is True:
    if is_send_seg:
        seg_cn_units = {
            "mask": "",
            "module": "none",
            "model": "diff_control_sd15_seg_fp16 [a1e85e27]",
            "weight": 1,
            "resize_mode": "Scale to Fit (Inner Fit)",
            "lowvram": False,
            "processor_res": 64,
            "threshold_a": 64,
            "threshold_b": 64,
            "guidance": 1,
            "guidance_start": 0,
            "guidance_end": 1,
            "guessmode": False,
        }
        with open(get_asset_path(before_output_seg_filename), "rb") as seg_file:
            seg_cn_units["input_image"] = base64.b64encode(seg_file.read()).decode()
        params["alwayson_scripts"]["controlnet"]["args"].append(seg_cn_units)

    # send to API
    output_file = actually_send_to_api(params, after_output_filename_prefix)

    # if we got a successful image created, load it into the scene
    if output_file:
        new_output_file = None

        # save the after image
        new_output_file = save_after_image(
            scene, after_output_filename_prefix, output_file
        )

        # if we saved a new output image, use it
        if new_output_file:
            output_file = new_output_file

        # load the image into image editor
        try:
            img = bpy.data.images.load(output_file, check_existing=False)
            for window in bpy.data.window_managers["WinMan"].windows:
                for area in window.screen.areas:
                    if area.type == "IMAGE_EDITOR":
                        area.spaces.active.image = img
        except:
            return print("Couldn't load the image.")

        return True
    else:
        return False


def actually_send_to_api(params, filename_prefix):
    # create headers
    headers = {
        "User-Agent": "Blender/" + bpy.app.version_string,
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
    }

    # prepare server url
    server_url = "http://localhost:7860" + "/sdapi/v1/txt2img"

    # send API request
    try:
        response = requests.post(server_url, json=params, headers=headers, timeout=1000)
    except requests.exceptions.ConnectionError:
        return print(f"The Automatic1111 server couldn't be found.")
    except requests.exceptions.MissingSchema:
        return print(f"The url for your Automatic1111 server is invalid.")
    except requests.exceptions.ReadTimeout:
        return print("The Automatic1111 server timed out.")

    # handle the response
    if response.status_code == 200:
        return handle_api_success(response, filename_prefix)
    else:
        return handle_api_error(response)


def handle_api_success(response, filename_prefix):
    try:
        response_obj = response.json()
        base64_img = response_obj["images"][0]
    except:
        print("Automatic1111 response content: ")
        print(response.content)
        return print("Received an unexpected response from the Automatic1111 server.")

    # create a temp file
    try:
        output_file = create_temp_file(filename_prefix + "-")
    except:
        return print("Couldn't create a temp file to save image.")

    # decode base64 image
    try:
        img_binary = base64.b64decode(base64_img.replace("data:image/png;base64,", ""))
    except:
        return print("Couldn't decode base64 image.")

    # save the image to the temp file
    try:
        with open(output_file, "wb") as file:
            file.write(img_binary)
    except:
        return print("Couldn't write to temp file.")

    # return the temp file
    return output_file


def handle_api_error(response):
    if response.status_code == 404:
        import json

        try:
            response_obj = response.json()
            if response_obj.get("detail") and response_obj["detail"] == "Not Found":
                return print(
                    "It looks like the Automatic1111 server is running, but it's not in API mode."
                )
            elif (
                response_obj.get("detail")
                and response_obj["detail"] == "Sampler not found"
            ):
                return print("The sampler you selected is not available.")
            else:
                return print(
                    f"An error occurred in the Automatic1111 server. Full server response: {json.dumps(response_obj)}"
                )
        except:
            return print(
                "It looks like the Automatic1111 server is running, but it's not in API mode."
            )
    else:
        print(response.content)
        return print("An error occurred in the Automatic1111 server.")


def create_temp_file(prefix, suffix=".png"):
    return tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix).name


def save_after_image(scene, filename_prefix, img_file):
    filename = f"{filename_prefix}.png"
    full_path_and_filename = os.path.join(
        os.path.abspath(bpy.path.abspath(IMAGE_FOLDER)), filename
    )
    try:
        copy_file(img_file, full_path_and_filename)
        return full_path_and_filename
    except:
        return print(
            f"Couldn't save 'after' image to {bpy.path.abspath(full_path_and_filename)}"
        )


def get_absolute_path(path):
    return os.path.abspath(bpy.path.abspath(path))


def get_asset_path(filename):
    return os.path.join(get_absolute_path(IMAGE_FOLDER), filename)


def get_output_width(scene):
    return round(scene.render.resolution_x * scene.render.resolution_percentage / 100)


def get_output_height(scene):
    return round(scene.render.resolution_y * scene.render.resolution_percentage / 100)


def copy_file(src, dest):
    shutil.copy2(src, dest)


bpy.app.handlers.render_complete.clear()
bpy.app.handlers.render_complete.append(render_complete_handler)
