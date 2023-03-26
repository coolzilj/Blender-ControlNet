# Blender-ControlNet

Using Multiple ControlNet in Blender.

## Required

- [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [Mikubill/sd-webui-controlnet](https://github.com/Mikubill/sd-webui-controlnet)

## Usage

### 1. Start A1111 in API mode.

First, of course, is to run web ui with `--api` commandline argument

- example in your "webui-user.bat": `set COMMANDLINE_ARGS=--api`

### 2. Install Mikubill/sd-webui-controlnet extension

You have to install the `Mikubill/sd-webui-controlnet` extension in A1111 and download the ControlNet models.  
Please refer to the installation instructions from [Mikubill/sd-webui-controlnet](https://github.com/Mikubill/sd-webui-controlnet).

**Notes**

- In new version of Mikubill/sd-webui-controlnet, you need to enable `Allow other script to control this extension` in settings for API access.
- To enable Multi ControlNet, change `Multi ControlNet: Max models amount (requires restart)` in the settings. Note that you will need to restart the WebUI for changes to take effect.

### 3. Copy and paste the `multicn.py` code into your blender Scripting pane.

### 4. How to use the script?

Basically, the script utilizes Blender Compositor to generate the required maps and then sends them to AUTOMATIC1111.

To generate the desired output, you need to make adjustments to either the code or Blender Compositor nodes before pressing `F12`. To simplify this process, I have provided a basic [Blender template](./blender_templates/multicn_depth%2Bseg.blend) that sends depth and segmentation maps to ControlNet.

Here is a brief [tutorial](https://twitter.com/Songzi39590361/status/1632706795365072897) on how to modify to suit @toyxyz3's rig if you wish to send openpose/depth/canny maps.

**Notes**

- Make sure you have the right name for `controlnet_model`, hash does matter. You can get your local installed ControlNet models list from [here](http://localhost:7860/docs#/default/model_list_controlnet_model_list_get).

### 5. Hit "Run Script"

Before you hit "Run Script", here are the parameters that you may want to modify in the scripts:

```
# specify your images output folder
IMAGE_FOLDER = "//sd_results"

# if you don't want to send your maps to AI, set this option to False
is_using_ai = True

# which maps are you going to send to AI
is_send_canny = False
is_send_depth = False
is_send_bone = True
is_send_seg = False

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
```

### 6. Hit **F12**, wait for it...

## Bonus

To create 150 ControlNet segmentation colors materials, run `seg.py`. Check out this [tweet](https://twitter.com/Songzi39590361/status/1631190450710409216) for instructions.

## Todo

- [ ] animation support
