from bpy.app.handlers import persistent
import bpy
import os
import shutil
import time
import tempfile
import base64
import requests

IMAGE_FOLDER = "path/to/image/folder"

DEFAULT_PARAMS = {
    "prompt": "1 girl dancing on the beach, ocean background, sunset glow, best quality",
    "negative_prompt": "worst quality, low quality, lowres, normal quality",
    "width": 512,
    "height": 512,
    "seed": -1,
    "subseed": -1,
    "subseed_strength": 0,
    "batch_size": 1,
    "n_iter": 1,
    "steps": 20,
    "cfg_scale": 7,
    "restore_faces": False,
    "sampler_index": "DPM++ 2M Karras",
    "controlnet_module": "depth",
    "controlnet_model": "diff_control_sd15_depth_fp16 [978ef0a1]",
    "controlnet_guidance": 1.0,
    "enable_hr": False,
    "denoising_strength": 0.5,
    "hr_scale": 2,
    "hr_upscale": "Latent (bicubic antialiased)",
}


@persistent
def render_complete_handler(scene):
    is_img_ready = bpy.data.images['Render Result'].has_data

    if is_img_ready:
        send_to_api(scene)
    else:
        print("Rendered image is not ready.")


def send_to_api(scene):
    # prepare output filenames
    timestamp = int(time.time())
    before_output_filename_prefix = f"{timestamp}-1-before"
    after_output_filename_prefix = f"{timestamp}-2-after"

    # save rendered image to temp and then read it back in
    temp_input_file = save_render_to_file(scene, before_output_filename_prefix)
    if not temp_input_file:
        return False
    img_file = open(temp_input_file, 'rb')

    # save the before image
    save_before_image(scene, before_output_filename_prefix)

    # prepare data for API
    params = DEFAULT_PARAMS

    params["controlnet_input_image"] = [
        base64.b64encode(img_file.read()).decode()]
    img_file.close()

    # send to API
    output_file = actually_send_to_api(params, after_output_filename_prefix)

    # if we got a successful image created, load it into the scene
    if output_file:
        new_output_file = None

        # save the after image
        new_output_file = save_after_image(
            scene, after_output_filename_prefix, output_file)

        # if we saved a new output image, use it
        if new_output_file:
            output_file = new_output_file

        # load the image into image editor
        try:
            img = bpy.data.images.load(output_file, check_existing=False)
            for window in bpy.data.window_managers['WinMan'].windows:
                for area in window.screen.areas:
                    if area.type == 'IMAGE_EDITOR':
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
    server_url = "http://localhost:7860" + "/controlnet/txt2img"

    # send API request
    try:
        response = requests.post(
            server_url, json=params, headers=headers, timeout=1000)
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
        img_binary = base64.b64decode(
            base64_img.replace("data:image/png;base64,", ""))
    except:
        return print("Couldn't decode base64 image.")

    # save the image to the temp file
    try:
        with open(output_file, 'wb') as file:
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
            if response_obj.get('detail') and response_obj['detail'] == "Not Found":
                return print("It looks like the Automatic1111 server is running, but it's not in API mode.")
            elif response_obj.get('detail') and response_obj['detail'] == "Sampler not found":
                return print("The sampler you selected is not available.")
            else:
                return print(f"An error occurred in the Automatic1111 server. Full server response: {json.dumps(response_obj)}")
        except:
            return print("It looks like the Automatic1111 server is running, but it's not in API mode.")
    else:
        return print("An error occurred in the Automatic1111 server.")


def create_temp_file(prefix, suffix=".png"):
    return tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix).name


def save_render_to_file(scene, filename_prefix):
    try:
        temp_file = create_temp_file(filename_prefix + "-", suffix=".png")
    except:
        return print("Couldn't create temp file for image")

    try:
        orig_render_file_format = scene.render.image_settings.file_format
        orig_render_color_mode = scene.render.image_settings.color_mode
        orig_render_color_depth = scene.render.image_settings.color_depth

        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '8'

        bpy.data.images['Render Result'].save_render(temp_file)

        scene.render.image_settings.file_format = orig_render_file_format
        scene.render.image_settings.color_mode = orig_render_color_mode
        scene.render.image_settings.color_depth = orig_render_color_depth
    except:
        return print("Couldn't save rendered image")

    return temp_file


def save_before_image(scene, filename_prefix):
    ext = ".png"
    filename = f"{filename_prefix}{ext}"
    full_path_and_filename = os.path.join(os.path.abspath(
        bpy.path.abspath(IMAGE_FOLDER)), filename)
    try:
        bpy.data.images['Render Result'].save_render(
            bpy.path.abspath(full_path_and_filename))
    except:
        return print(f"Couldn't save 'before' image to {bpy.path.abspath(full_path_and_filename)}")


def save_after_image(scene, filename_prefix, img_file):
    filename = f"{filename_prefix}.png"
    full_path_and_filename = os.path.join(os.path.abspath(
        bpy.path.abspath(IMAGE_FOLDER)), filename)
    try:
        copy_file(img_file, full_path_and_filename)
        return full_path_and_filename
    except:
        return print(f"Couldn't save 'after' image to {bpy.path.abspath(full_path_and_filename)}")


def get_output_width(scene):
    return round(scene.render.resolution_x * scene.render.resolution_percentage / 100)


def get_output_height(scene):
    return round(scene.render.resolution_y * scene.render.resolution_percentage / 100)


def copy_file(src, dest):
    shutil.copy2(src, dest)


bpy.app.handlers.render_complete.clear()
bpy.app.handlers.render_complete.append(render_complete_handler)
