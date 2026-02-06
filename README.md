# 🔒 보안 PDF 마스킹 도구 (Secure PDF Masking Tool)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()

PDF 문서에서 특정 텍스트를 검정 박스로 마스킹하여 **개인정보를 안전하게 보호**하는 Windows용 도구입니다.

![Screenshot](screenshot.png)

## ⚠️ 보안 기능

이 도구는 **PyMuPDF의 Redaction 기능**을 사용하여 원본 텍스트 데이터를 **완전히 제거**합니다.

- ✅ 일반적인 '덮어쓰기' 방식과 다름
- ✅ 원본 데이터가 PDF 내부 구조에서 완전히 삭제
- ✅ AI나 텍스트 추출 도구로도 **복구 불가능**

## 📋 주요 기능

| 기능 | 설명 |
|------|------|
| 🔒 **텍스트 마스킹** | 지정한 텍스트를 검정 박스로 완전히 가림 |
| ✏️ **직접 입력** | 마스킹할 텍스트를 하나씩 직접 입력 |
| 📋 **일괄 입력** | TXT/CSV 파일에서 마스킹할 텍스트 목록 한번에 불러오기 |
| 📥 **양식 다운로드** | CSV 양식 파일을 다운로드하여 쉽게 목록 작성 |
| 🇰🇷 **한글 지원** | 한글 텍스트 검색 및 마스킹 완벽 지원 |
| 📊 **처리 로그** | 실시간 처리 현황 확인 |

## 🚀 다운로드 및 실행

### 방법 1: 실행 파일 다운로드 (권장)

1. [Releases](../../releases) 페이지에서 최신 버전 다운로드
2. `SecurePDFMasking.zip` 압축 해제
3. `SecurePDFMasking.exe` 실행

> Python 설치 없이 바로 사용 가능!

### 방법 2: 소스코드에서 실행

```powershell
# 저장소 클론
git clone https://github.com/YOUR_USERNAME/secure-pdf-masking.git
cd secure-pdf-masking

# 패키지 설치
pip install -r requirements.txt

# 실행
python secure_pdf_editor.py
```

## 📖 사용 방법

### 1. 파일 선택

"파일 선택" 버튼을 클릭하여 마스킹할 PDF를 선택합니다.

### 2. 마스킹할 텍스트 입력

**직접 입력 (왼쪽 패널):**

- 텍스트 입력란에 마스킹할 단어 입력 (예: `홍길동`, `서울고등학교`)
- "추가" 버튼 클릭 또는 Enter 키 입력

**일괄 입력 (오른쪽 패널):**

1. **📥 양식 다운로드** 버튼 클릭 → CSV 파일 저장
2. 엑셀로 열어 첫 번째 열에 마스킹할 텍스트 입력
3. 저장 후 **📂 리스트 불러오기** 버튼으로 불러오기

### 3. 마스킹 시작

"🔒 마스킹 시작" 버튼을 클릭합니다.

### 4. 결과 확인

같은 폴더에 `원본파일명_secure.pdf` 파일이 생성됩니다.

## 📁 지원 파일 형식

### TXT 파일

```
홍길동
김철수
서울고등학교
010-1234-5678
```

### CSV 파일

```csv
마스킹할_텍스트,비고
홍길동,이름
서울고등학교,학교명
```

## ⚙️ 시스템 요구사항

- **운영체제**: Windows 10/11
- **Python**: 3.8 이상 (소스에서 실행 시)
- **필수 라이브러리**: PyMuPDF

## 🔧 문제 해결

### 텍스트가 검색되지 않는 경우

- PDF가 OCR 처리되어 선택 가능한 텍스트가 있는지 확인하세요.
- 이미지 기반 PDF는 텍스트 검색이 불가능합니다.

### 프로그램이 실행되지 않는 경우

```powershell
pip uninstall pymupdf
pip install pymupdf
```

## 📝 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE)를 따릅니다.

## 🛡️ 주의사항

- ⚠️ 원본 PDF 파일은 백업해 두세요
- ⚠️ 변환된 파일에서는 원본 내용 복구가 **불가능**합니다
- ⚠️ 중요한 문서는 변환 후 반드시 내용을 확인하세요

## 🤝 기여하기

버그 리포트, 기능 제안, Pull Request를 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
