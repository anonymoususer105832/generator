# %% [1] 이미지 크롭 및 마우스 클릭 수집 셀
%matplotlib qt
# 만약 qt가 에러나면 %matplotlib widget 사용 (ipympl 설치 필요)

import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np
import cv2
import torch
from tkinter import filedialog, Tk

import os
from segment_anything import sam_model_registry, SamPredictor
#%%
# 체크포인트 파일명에 맞게 model_type을 'vit_b'로 수정했습니다.
sam_checkpoint = "./sam_vit_b_01ec64.pth" 
model_type = "vit_b" 
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"📦 모델 로드 중... ({device})")
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)
predictor = SamPredictor(sam)
print(" 모델 로드 완료")

#%%
# 데이터 초기화 (전역 변수)
coords_list = []
labels_list = []
crop_coords = None
cropped_image_rgb = None

def run_masking_ui():
    global cropped_image_rgb, predictor, coords_list, labels_list, crop_coords
    
    # 1. 파일 열기
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    # file_path = filedialog.askopenfilename(title="이미지 선택")
    file_path = r"C:\Users\user\jupyter\photos\original.jpg"

    
    root.destroy()

    if not file_path: 
        print("❌ 이미지가 선택되지 않았습니다.")
        return

    image_bgr = cv2.imread(file_path)
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    # ---------------------------------------------------------
    # 2. 크롭 영역 선택 UI
    # ---------------------------------------------------------
    crop_coords = None
    plt.close('all')
    fig_crop, ax_crop = plt.subplots(figsize=(10, 8))
    ax_crop.imshow(image_rgb)
    ax_crop.set_title("Draw a rectangle to CROP / Close window when done")

    def onselect(eclick, erelease):
        global crop_coords
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        crop_coords = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

    # 드래그로 사각형 그리기 활성화
    rs = RectangleSelector(ax_crop, onselect, interactive=True,
                           button=[1], minspanx=5, minspany=5, spancoords='pixels')
    plt.show(block=True) # 창을 닫을 때까지 대기

    # 크롭 적용
    if crop_coords:
        x1, y1, x2, y2 = crop_coords
        cropped_image_rgb = image_rgb[y1:y2, x1:x2]
        print(f"이미지 크롭 완료: {crop_coords}")
    else:
        cropped_image_rgb = image_rgb.copy()
        print("크롭 없이 원본 이미지를 그대로 사용합니다.")

    # ---------------------------------------------------------
    # 3. SAM 마스킹 UI 
    # ---------------------------------------------------------
    coords_list.clear()
    labels_list.clear()
    
    # SAM 모델에 '크롭된 이미지' 설정
    print("SAM 모델 특징 추출 중... (잠시만 기다려 주세요)")
    predictor.set_image(cropped_image_rgb) 

    fig_mask, ax_mask = plt.subplots(figsize=(10, 8))
    ax_mask.imshow(cropped_image_rgb)
    ax_mask.set_title("Left: Add / Right: Remove / Close window when done")

    def onclick(event):
        if event.xdata is None or event.ydata is None: return
        label = 1 if event.button == 1 else 0
        ix, iy = int(event.xdata), int(event.ydata)
        
        coords_list.append([ix, iy])
        labels_list.append(label)
        
        color = 'lime' if label == 1 else 'red'
        ax_mask.scatter(ix, iy, color=color, s=50, edgecolors='white')
        fig_mask.canvas.draw()

    fig_mask.canvas.mpl_connect('button_press_event', onclick)
    plt.show(block=True)

run_masking_ui()


if 'cropped_image_rgb' in globals() and cropped_image_rgb is not None:
    cropped_bgr = cv2.cvtColor(cropped_image_rgb, cv2.COLOR_RGB2BGR)
    cv2.imwrite("original.jpg", cropped_bgr)
    print("📸 크롭된 원본이 'original.jpg'로 저장되었습니다.")

    if len(coords_list) > 0:
        # 2. SAM 추론 (크롭된 이미지 위에 찍힌 좌표 기준)
        masks, scores, _ = predictor.predict(
            point_coords=np.array(coords_list),
            point_labels=np.array(labels_list),
            multimask_output=False,
        )
        
        # 3. 마스크 이진화 (0 또는 255)
        final_mask = np.zeros(cropped_image_rgb.shape[:2], dtype=np.uint8)
        final_mask[masks[0] == True] = 255 
        
        h, w = cropped_image_rgb.shape[:2]
        margin = int(min(h, w) / 200)   
        kernel_size = max(1, (margin * 2) + 1)  
        
        print(f" 동적 마스크 팽창 적용: {kernel_size})")
        
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        final_mask = cv2.dilate(final_mask, kernel, iterations=1)


        # 4. 마스크 저장
        cv2.imwrite("mask2.png", final_mask)
        print("마스크 파일 'mask2.png'로 저장")

        # 5. 최종 시각화 확인
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1); plt.imshow(cropped_image_rgb); plt.title("Saved: original.jpg")
        plt.subplot(1, 2, 2); plt.imshow(final_mask, cmap='gray'); plt.title("Saved: masked.png")
        plt.show()
    else:
        print("⚠️ 선택된 마킹 좌표가 없어 마스크를 생성하지 않았습니다.")
else:
    print("❌ 크롭된 이미지 데이터가 없습니다. [1]번 셀을 먼저 실행해 주세요.")