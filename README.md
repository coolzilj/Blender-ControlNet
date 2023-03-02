# Blender-ControlNet

A quick demo script for you using ControlNet without leaving Blender.

## Required

- [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [Mikubill/sd-webui-controlnet](https://github.com/Mikubill/sd-webui-controlnet)

## Usage

For now, it's just a quick and hardcoded script.

### 0. Start A1111 in API mode.
You have to install the `Mikubill/sd-webui-controlnet` extension in A1111 and download the ControlNet models first, please refer to the installation instructions from [Mikubill/sd-webui-controlnet](https://github.com/Mikubill/sd-webui-controlnet).

**Notes**
- In new version of Mikubill/sd-webui-controlnet, you need to enable `Allow other script to control this extension` in settings for API access.

### 1. Copy and paste the `demo.py` code into your blender Scripting pane.

### 2. Below is the default params, tweak as you like.

```
DEFAULT_PARAMS = {
    "prompt": "...",
    "negative_prompt": "...",
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
```

and don't forget to modify the image saving folder.

```
IMAGE_FOLDER = "F:\\PATH\\DOESNT\\EXIST\\YET"
```

**Notes**
- Make sure you have the right name for `controlnet_model`, hash does matter. You can get your local installed ControlNet models list from [here](http://localhost:7860/docs#/default/model_list_controlnet_model_list_get).

### 3. Hit "Run Script"

![](./assets/1.png)

### 4. Hit **F12**, wait for it...

## Roadmap

- [ ] Blender addon
