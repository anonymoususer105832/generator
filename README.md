배포를 전제하지 않고 만든 파일이라 작성자의 개인 환경에 맞춰져 있고, 개보수도 불편함.

mask1로 수정하고 싶은 것의 전체를 마스킹. 차의 본넷을 수정하고 싶다면 일단 차 전체를 여러군데 클릭해서 마스킹함.

mask2는 수정하고 싶은 것만 마스킹. 차의 본넷을 수정하고 싶다면 본넷만 수정

additional_mask1에서, 마스크가 전체적으로 발려지지 않았다면 클릭해서 추가로 바름. 마스크가 외부로 뻗어나가 있다면 우클릭으로 제거.

additional_mask2에서, 마스크가 적용될 부분을 세부적으로 수정.



openvino 사용(gpu X) 전제하고 만든 파일. gpu가 있다면 torch gpu버전을 다운받고 해당 부분을 수정하면 됨.

아니라면, 사용할 모델을 다운받고 openvino_setup로 해당 모델 safetensor 파일을 openvino로 컴포팅하면 됨.

Huggingface나 Civitai같은 곳에서 safetensor 다운로드 가능. inpainting이 목적이므로 해당 모델들을 다운받는 것을 추천함.
