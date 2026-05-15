#%%

import cv2
import numpy as np
import os

# ---------------------------------------------------------
# 🛠️ [설정] 파일 경로 (환경에 맞게 수정)
# ---------------------------------------------------------
# 1. 원본 이미지 파일 경로 (필수!)
INPUT_ORIGINAL_PATH = "original.jpg" # 👈 원본 사진 경로

# 2. 기존 마스크 파일 경로
INPUT_MASK_PATH = "mask2_updated.png"

# 3. 수정 후 저장될 마스크 파일 경로
OUTPUT_MASK_PATH = "mask2_updated.png"

# 붓 크기 (조절 가능)
BRUSH_SIZE = 7

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
        # --- [핵심!] 오버레이 생성 로직 ---
        # 1. 마스크 이미지를 BGR 컬러 공간으로 변환 (원본과 합성하기 위해)
        mask_bgr = cv2.cvtColor(img_mask, cv2.COLOR_GRAY2BGR)
        
        # 2. 마스크된 부분(흰색)을 붉은색(0, 0, 255)으로 바꾸기
        # 마스크 이미지에서 흰색(255)인 부분만 붉은색으로 설정합니다.
        colored_mask = np.zeros_like(img_orig)
        colored_mask[img_mask == 255] = (0, 0, 255) # BGR 순서 (Blue, Green, Red)
        
        # 3. 원본 이미지와 붉은색 마스크를 합성
        # 원본 이미지 비율: 1.0 (그대로 사용)
        # 붉은색 마스크 비율: 0.3 (투명도)
        # 마지막 0은 가중치 합에 더하는 상숫값
        img_show = cv2.addWeighted(img_orig, 1.0, colored_mask, 0.5, 0)
        
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
import cv2
import numpy as np
import os

# ---------------------------------------------------------
# 🛠️ [설정] 파일 경로
# ---------------------------------------------------------


# 상태 변수
BRUSH_SIZE = 13
drawing = False
mode = True

# 🎯 [추가] 줌(Zoom) 및 패닝(Pan) 상태 변수
zoom = 1.0
pan_x = 0
pan_y = 0
is_panning = False
pan_start_x = 0
pan_start_y = 0

def draw_mask(event, x, y, flags, param):
    global drawing, mode, BRUSH_SIZE
    global zoom, pan_x, pan_y, is_panning, pan_start_x, pan_start_y

    img_mask = param['img']
    h, w = img_mask.shape

    # 🎯 핵심: 화면에 보이는 좌표(x, y)를 원본 이미지의 실제 좌표(real_x, real_y)로 역산
    real_x = int(x / zoom) + pan_x
    real_y = int(y / zoom) + pan_y

    # 1. 줌인 / 줌아웃 (마우스 휠)
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0: # 휠을 위로 (확대)
            new_zoom = zoom * 1.2
        else:         # 휠을 아래로 (축소)
            new_zoom = zoom / 1.2

        new_zoom = max(1.0, min(new_zoom, 20.0)) # 1배 ~ 20배 제한

        # 마우스 커서가 있는 위치를 향해 확대되도록 pan 위치 재조정
        if new_zoom != zoom:
            pan_x = int(real_x - (x / new_zoom))
            pan_y = int(real_y - (y / new_zoom))
            zoom = new_zoom

    # 2. 화면 이동 / 패닝 (마우스 가운데 휠 버튼 클릭 & 드래그)
    elif event == cv2.EVENT_MBUTTONDOWN:
        is_panning = True
        pan_start_x, pan_start_y = x, y
    elif event == cv2.EVENT_MBUTTONUP:
        is_panning = False
    elif event == cv2.EVENT_MOUSEMOVE and is_panning:
        dx = x - pan_start_x
        dy = y - pan_start_y
        pan_x -= int(dx / zoom)
        pan_y -= int(dy / zoom)
        pan_start_x, pan_start_y = x, y

    # 3. 덧칠 및 지우기 (마우스 좌/우 클릭)
    elif event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        mode = True
        # 확대 시 붓 크기를 비례해서 줄여주어 정밀한 작업이 가능하게 함
        brush_r = max(1, int(BRUSH_SIZE / zoom))
        cv2.circle(img_mask, (real_x, real_y), brush_r, 255, -1)
    elif event == cv2.EVENT_RBUTTONDOWN:
        drawing = True
        mode = False
        brush_r = max(1, int(BRUSH_SIZE / zoom))
        cv2.circle(img_mask, (real_x, real_y), brush_r, 0, -1)
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        color = 255 if mode else 0
        brush_r = max(1, int(BRUSH_SIZE / zoom))
        cv2.circle(img_mask, (real_x, real_y), brush_r, color, -1)
    elif event == cv2.EVENT_LBUTTONUP or event == cv2.EVENT_RBUTTONUP:
        drawing = False

    # 패닝 시 이미지가 화면 밖으로 완전히 벗어나지 않도록 좌표 제한
    max_pan_x = int(w - (w / zoom))
    max_pan_y = int(h - (h / zoom))
    pan_x = max(0, min(pan_x, max_pan_x))
    pan_y = max(0, min(pan_y, max_pan_y))

def run_mask_editor():
    global zoom, BRUSH_SIZE, pan_x, pan_y
    
    if not os.path.exists(INPUT_ORIGINAL_PATH):
        print(f"❌ 에러: 원본 이미지 {INPUT_ORIGINAL_PATH}를 찾을 수 없습니다.")
        return
    if not os.path.exists(INPUT_MASK_PATH):
        print(f"❌ 에러: 마스크 이미지 {INPUT_MASK_PATH}를 찾을 수 없습니다.")
        return

    img_orig = cv2.imread(INPUT_ORIGINAL_PATH)
    img_mask = cv2.imread(INPUT_MASK_PATH, cv2.IMREAD_GRAYSCALE)

    if img_orig.shape[:2] != img_mask.shape:
        img_mask = cv2.resize(img_mask, (img_orig.shape[1], img_orig.shape[0]), interpolation=cv2.INTER_NEAREST)

    window_name = 'Precision Mask Editor'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    param = {'img': img_mask}
    cv2.setMouseCallback(window_name, draw_mask, param)

    print("\n 정밀 오버레이 마스크 수정 모드")
    print("- [좌클릭/우클릭] : 흰색 덧칠 / 검은색 지우기")
    print("- [마우스 휠]     : 마우스 커서 기준 확대/축소")
    print("- [휠 버튼 드래그]: 화면 이동 (패닝)")
    print("- 키보드 [ , ]    : 브러시 크기 감소/증가")
    print("- 키보드 +, -     : 줌 인/아웃 (마우스 휠 대체용)")
    print("- 키보드 [S]      : 마스크 저장 후 종료")
    print("- 키보드 [Q]      : 저장하지 않고 종료")

    while True:
        # 1. 마스크 오버레이 합성
        colored_mask = np.zeros_like(img_orig)
        colored_mask[img_mask == 255] = (0, 0, 255)
        img_show = cv2.addWeighted(img_orig, 1.0, colored_mask, 3.0, 0)

        # 2. 🎯 현재 줌/팬 상태에 맞춰 화면을 잘라내고(ROI) 확대
        h, w = img_show.shape[:2]
        view_w = int(w / zoom)
        view_h = int(h / zoom)

        # 보여줄 영역 잘라내기
        roi = img_show[pan_y : pan_y + view_h, pan_x : pan_x + view_w]

        # 창 크기(원본 해상도)에 맞춰 다시 확대
        display_img = cv2.resize(roi, (w, h), interpolation=cv2.INTER_LINEAR)

        # 왼쪽 상단에 현재 상태 텍스트 표시
        cv2.putText(display_img, f"Zoom: {zoom:.1f}x | Brush: {BRUSH_SIZE}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow(window_name, display_img)

        # 3. 키보드 단축키 이벤트 처리
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            cv2.imwrite(OUTPUT_MASK_PATH, img_mask)
            print(f"✨ 성공: 수정된 마스크가 저장되었습니다 -> {OUTPUT_MASK_PATH}")
            break
        elif key == ord('q'):
            print("👋 수정을 취소하고 종료합니다.")
            break
            
        # 단축키: 확대/축소 (+, -)
        elif key == ord('=') or key == ord('+'): 
            zoom = min(zoom * 1.2, 20.0)
        elif key == ord('-'):
            zoom = max(zoom / 1.2, 1.0)
            # 축소 시 화면 밖으로 나가는 것 보정
            max_pan_x = int(w - (w / zoom))
            max_pan_y = int(h - (h / zoom))
            pan_x = max(0, min(pan_x, max_pan_x))
            pan_y = max(0, min(pan_y, max_pan_y))
            
        # 단축키: 브러시 크기 조절 ([, ])
        elif key == ord('['):
            BRUSH_SIZE = max(1, BRUSH_SIZE - 2)
        elif key == ord(']'):
            BRUSH_SIZE = min(100, BRUSH_SIZE + 2)

    cv2.destroyAllWindows()

INPUT_ORIGINAL_PATH = "original.jpg" 

T= True
F= False

retouch = F
# 모델을 출력해 보고 mask를 수정할 필요가 있으면 T로 수정.

if retouch:
    INPUT_MASK_PATH = "mask2_updated.png"
else:
    INPUT_MASK_PATH = 'mask2.png'
OUTPUT_MASK_PATH = "mask2_updated.png"

if __name__ == "__main__":
    run_mask_editor()
