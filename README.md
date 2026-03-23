# usb-info-lnk-parser

### USB 연결 및 타임라인 추출

레지스트리 접근 (winreg): SYSTEM\CurrentControlSet\Enum\USBSTOR 경로를 순회하며 연결된 장치의 제조사, 모델명, 시리얼 넘버를 추출했습니다. 부가적으로 SOFTWARE\Microsoft\Windows Portable Devices\Devices 키를 대조하여 장치의 'Friendly Name'을 확보했습니다.

타임스탬프 변환 로직: USB의 최초 설치, 최근 연결, 제거 시간은 Properties\{83da6326-97a6-4088-9453-a1923f573b29} 하위의 0064, 0066, 0067 키에 바이너리 데이터로 저장됩니다. 이를 읽어와 1601년 기준의 100 나노초 단위 윈도우 타임스탬프(Little-Endian)를 파이썬의 datetime 객체로 역산하고 KST(+9시간)로 보정하는 로직(raw_to_time)을 구현했습니다.

### LNK 파일 파싱

바이너리 파싱 및 인코딩 처리: .lnk 파일은 단순 텍스트가 아니므로 LnkParse3를 활용해 내부 구조를 파싱했습니다. 이를 통해 원본 파일 경로와 접근 시간을 추출할 수 있었습니다.

### 핵심 기능

USB Registry 파싱: SYSTEM\CurrentControlSet\Enum\USBSTOR 등을 분석해 장치명, 시리얼, 최초/최근 연결 시간 추출.
LNK 파일 파싱: C:\Users\...\Recent 폴더 내의 .lnk 파일을 분석(LnkParse3 활용)하여 원본 파일 경로와 접근 시간 추출.
