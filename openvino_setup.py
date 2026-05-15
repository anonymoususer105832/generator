#%%
from diffusers import StableDiffusionPipeline
from optimum.intel import OVStableDiffusionPipeline
import shutil

# 1. 경로 설정
safetensors_path = "./meinahentai_v4-inpainting.safetensors" # 다운받은 모델 경로
temp_diffusers_path = "./models/temp_diffusers"       # 임시 변환 폴더
openvino_save_path = "./models/meinahentai_openvino"  # 최종 OpenVINO 모델 폴더

print("safetensors 파일을 일반 diffusers 포맷으로 로드 중...")
pipe = StableDiffusionPipeline.from_single_file(safetensors_path)
pipe.save_pretrained(temp_diffusers_path)

print("OpenVINO 포맷(IR)으로 컴파일 및 변환 중")
ov_pipe = OVStableDiffusionPipeline.from_pretrained(
    temp_diffusers_path, 
    export=True, 
    compile=False 
)

print("변환된 OpenVINO 모델 저장")
ov_pipe.save_pretrained(openvino_save_path)

# (선택) 임시로 만든 diffusers 폴더 삭제
shutil.rmtree(temp_diffusers_path)


#%%
from optimum.intel import OVStableDiffusionInpaintPipeline

# export=False 로 설정
pipeline = OVStableDiffusionInpaintPipeline.from_pretrained(
    "./models/meinahentai_openvino", 
    export=False,
    compile=True
)