#%%

import cv2
import numpy as np
import os

# ---------------------------------------------------------
# 🛠️ [설정] 파일 경로 (환경에 맞게 수)
# ---------------------------------------------------------
# 1. 원본 이미지 파일 경로
INPUT_ORIGINAL_PATH = "original.jpg" # 원본 사진 경로

# 2. 기존 마스크 파일 경로
INPUT_MASK_PATH = "mask1.png"

# 3. 수정 후 저장될 마스크 파일 경로
OUTPUT_MASK_PATH = "mask1_updated.png"

# 붓 크기 (조절 가능)
BRUSH_SIZE = 20

# ---------------------------------------------------------
# 🐭 마우스 콜백 함수 정의
# ---------------------------------------------------------
drawing = False # 마우스가 눌렸는지 확인하는 플래그
mode = True # True: 덧칠(흰색), False: 지우기(검은색)

def draw_mask(event, x, y, flags, param):
    global drawing, mode, BRUSH_SIZE
    
    # 수정할 마스크 이미지 (글로벌 변수 참조)
    img_mask = param['img']

    if event == cv2.EVENT_LBUTTONDOWN: # 왼쪽 버튼: 덧칠 시작
        drawing = True
        mode = True
    elif event == cv2.EVENT_RBUTTONDOWN: # 오른쪽 버튼: 지우기 시작
        drawing = True
        mode = False
        
    elif event == cv2.EVENT_MOUSEMOVE: # 마우스 이동 시
        if drawing == True:
            color = 255 if mode else 0 # 흑백 이미지이므로 단일 값 사용
            # 원형 붓으로 그리기
            cv2.circle(img_mask, (x, y), BRUSH_SIZE, color, -1)
            
    elif event == cv2.EVENT_LBUTTONUP or event == cv2.EVENT_RBUTTONUP: # 버튼 뗌
        drawing = False

# ---------------------------------------------------------
# 🚀 메인 실행 함수
# ---------------------------------------------------------
def run_mask_editor():
    # 1. 파일 로드 확인
    if not os.path.exists(INPUT_ORIGINAL_PATH):
        print(f"❌ 에러: 원본 이미지 {INPUT_ORIGINAL_PATH} 파일을 찾을 수 없습니다.")
        return

    if not os.path.exists(INPUT_MASK_PATH):
        print(f"❌ 에러: 마스크 이미지 {INPUT_MASK_PATH} 파일을 찾을 수 없습니다.")
        return

    # 2. 이미지 로드
    # 원본은 컬러로, 마스크는 흑백으로 불러옵니다.
    img_orig = cv2.imread(INPUT_ORIGINAL_PATH)
    img_mask = cv2.imread(INPUT_MASK_PATH, cv2.IMREAD_GRAYSCALE)
    
    # 두 이미지 크기가 다르면 마스크 크기를 원본에 맞춥니다.
    if img_orig.shape[:2] != img_mask.shape:
        img_mask = cv2.resize(img_mask, (img_orig.shape[1], img_orig.shape[0]), interpolation=cv2.INTER_NEAREST)

    # 3. 윈도우 생성 및 마우스 콜백 연결
    window_name = 'Mask Editor (L:Add, R:Erase, S:Save, Q:Quit)'
    cv2.namedWindow(window_name)
    # 콜백 함수에 마스크 이미지를 전달하기 위해 파라미터 딕셔너리 사용
    param = {'img': img_mask}
    cv2.setMouseCallback(window_name, draw_mask, param)

    print("\n🖌️ 오버레이 마스크 수정 모드를 시작합니다.")
    print("- 마우스 왼쪽 버튼: 흰색으로 덧칠 (Mask 추가)")
    print("- 마우스 오른쪽 버튼: 검은색으로 지우기 (Mask 제거, 원본 보임)")
    print("- 키보드 [S]: 수정된 마스크 저장 후 종료")
    print("- 키보드 [Q]: 저장하지 않고 종료")

    # 4. 메인 루프 (화면 갱신)
    while True:
        # 1. 마스크 이미지를 BGR 컬러 공간으로 변환
        mask_bgr = cv2.cvtColor(img_mask, cv2.COLOR_GRAY2BGR)
        
        # 2. 마스크된 부분(흰색)을 붉은색(0, 0, 255)으로 바꾸기
        colored_mask = np.zeros_like(img_orig)
        colored_mask[img_mask == 255] = (0, 0, 255) # BGR 순서 (Blue, Green, Red)
        
        # 3. 원본 이미지와 붉은색 마스크를 합성
        # 원본 이미지 비율: 1.0 (그대로 사용)
        # 붉은색 마스크 비율: 0.3 (투명도)
        # 마지막 0은 가중치 합에 더하는 상숫값
        img_show = cv2.addWeighted(img_orig, 1.0, colored_mask, 0.8, 0)
        
        # 현재 마스크 상태를 원본과 겹쳐서 보여줍니다.
        cv2.imshow(window_name, img_show)
        
        key = cv2.waitKey(1) & 0xFF
        
        # 's' 키: 저장 (오버레이가 아닌, 실제 수정한 흑백 마스크를 저장해야 함)
        if key == ord('s'):
            cv2.imwrite(OUTPUT_MASK_PATH, img_mask)
            print(f"✨ 수정된 마스크가 저장되었습니다: {OUTPUT_MASK_PATH}")
            break
            
        # 'q' 키: 종료
        elif key == ord('q'):
            print("👋 수정을 취소하고 종료합니다.")
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_mask_editor()
    
# %%
print('done')
# %%
