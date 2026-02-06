"""
보안 PDF 편집기 (Secure PDF Redaction & Editor Tool)
====================================================
- 텍스트 검색 및 완전 삭제 후 대체 텍스트 삽입
- 이름 마스킹 기능 (예: 홍길동 → ㅁㅁㅁ)
- PyMuPDF의 Redaction 기능을 사용하여 원본 데이터 완전 제거
- 한글 UI 및 한글 폰트 지원

Author: AI Assistant
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import fitz  # PyMuPDF
import os
import csv
from pathlib import Path
from typing import List, Tuple, Dict
import threading


class SecurePDFEditor:
    """보안 PDF 편집기 메인 클래스"""
    
    # 한글 폰트 경로 (Windows)
    KOREAN_FONTS = [
        "C:/Windows/Fonts/malgun.ttf",      # 맑은 고딕
        "C:/Windows/Fonts/malgunbd.ttf",    # 맑은 고딕 Bold
        "C:/Windows/Fonts/gulim.ttc",       # 굴림
        "C:/Windows/Fonts/batang.ttc",      # 바탕
        "C:/Windows/Fonts/NanumGothic.ttf", # 나눔고딕
    ]
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("보안 PDF 마스킹 도구 - Secure PDF Masking Tool")
        self.root.geometry("900x750")
        self.root.minsize(800, 650)
        
        # 변수 초기화
        self.pdf_path: str = ""
        self.direct_mask_list: List[str] = []  # 직접 입력한 마스킹 텍스트
        self.batch_mask_list: List[str] = []   # 일괄 입력한 마스킹 텍스트
        self.korean_font_path: str = self._find_korean_font()
        
        # UI 스타일 설정
        self._setup_styles()
        
        # UI 구성
        self._create_widgets()
        
        # 로그 초기 메시지
        self._log("프로그램이 시작되었습니다.")
        self._log(f"한글 폰트: {self.korean_font_path or '찾을 수 없음'}")
    
    def _find_korean_font(self) -> str:
        """시스템에서 사용 가능한 한글 폰트 찾기"""
        for font_path in self.KOREAN_FONTS:
            if os.path.exists(font_path):
                return font_path
        return ""
    
    def _setup_styles(self):
        """UI 스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 버튼 스타일
        style.configure('Primary.TButton', 
                       font=('맑은 고딕', 11, 'bold'),
                       padding=(20, 10))
        style.configure('Secondary.TButton',
                       font=('맑은 고딕', 9),
                       padding=(10, 5))
        style.configure('Action.TButton',
                       font=('맑은 고딕', 14, 'bold'),
                       padding=(30, 15))
        
        # 라벨 스타일
        style.configure('Header.TLabel',
                       font=('맑은 고딕', 12, 'bold'))
        style.configure('Normal.TLabel',
                       font=('맑은 고딕', 10))
        
        # 프레임 스타일
        style.configure('Card.TFrame',
                       relief='solid',
                       borderwidth=1)
    
    def _create_widgets(self):
        """UI 위젯 생성"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.root, padding="15")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # === 파일 선택 섹션 ===
        self._create_file_section(main_container)
        
        # === 설정 영역 ===
        settings_frame = ttk.Frame(main_container)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 왼쪽: 마스킹할 텍스트 직접 입력
        left_frame = ttk.LabelFrame(settings_frame, text="✏️ 마스킹할 텍스트 직접 입력", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self._create_direct_mask_section(left_frame)
        
        # 오른쪽: 마스킹할 텍스트 일괄 입력
        right_frame = ttk.LabelFrame(settings_frame, text="📋 마스킹할 텍스트 일괄 입력", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self._create_batch_mask_section(right_frame)
        
        # === 실행 버튼 ===
        self._create_action_section(main_container)
        
        # === 로그 영역 ===
        self._create_log_section(main_container)
    
    def _create_file_section(self, parent):
        """파일 선택 섹션 생성"""
        file_frame = ttk.LabelFrame(parent, text="📁 PDF 파일", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 파일 경로 표시
        self.file_path_var = tk.StringVar(value="파일을 선택해주세요...")
        path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, 
                              state='readonly', font=('맑은 고딕', 10))
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # 파일 선택 버튼
        select_btn = ttk.Button(file_frame, text="파일 선택", 
                               style='Primary.TButton',
                               command=self._select_file)
        select_btn.pack(side=tk.RIGHT)
    
    def _create_direct_mask_section(self, parent):
        """마스킹할 텍스트 직접 입력 섹션"""
        # 안내 문구
        guide_frame = ttk.Frame(parent)
        guide_frame.pack(fill=tk.X, pady=(0, 10))
        
        guide_text = "마스킹할 텍스트를 직접 입력하고 추가 버튼을 누르세요."
        ttk.Label(guide_frame, text=guide_text, 
                 font=('맑은 고딕', 9), foreground='gray').pack(anchor=tk.W)
        
        # 입력 영역
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="텍스트:", 
                 style='Normal.TLabel').pack(side=tk.LEFT)
        self.direct_mask_entry = ttk.Entry(input_frame, width=25, font=('맑은 고딕', 10))
        self.direct_mask_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Enter 키로 추가
        self.direct_mask_entry.bind('<Return>', lambda e: self._add_direct_mask())
        
        # 버튼 영역
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="➕ 추가", style='Secondary.TButton',
                  command=self._add_direct_mask).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="➖ 삭제", style='Secondary.TButton',
                  command=self._remove_direct_mask).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🗑️ 전체 삭제", style='Secondary.TButton',
                  command=self._clear_direct_masks).pack(side=tk.LEFT)
        
        # 리스트 영역
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.direct_mask_listbox = tk.Listbox(list_frame, height=8, 
                                              font=('맑은 고딕', 9),
                                              selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.direct_mask_listbox.yview)
        self.direct_mask_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.direct_mask_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_batch_mask_section(self, parent):
        """마스킹할 텍스트 일괄 입력 섹션"""
        # 안내 문구
        guide_frame = ttk.Frame(parent)
        guide_frame.pack(fill=tk.X, pady=(0, 10))
        
        guide_lines = [
            "📌 사용 방법:",
            "1. '양식 다운로드' 버튼을 눌러 CSV 파일을 저장",
            "2. 엑셀로 열어 첫 번째 열에 마스킹할 텍스트 입력",
            "3. 저장 후 '리스트 불러오기'로 불러오기",
            "",
            "💡 TXT 파일도 지원 (한 줄에 하나씩 입력)"
        ]
        for line in guide_lines:
            fg_color = '#0066cc' if line.startswith('📌') or line.startswith('💡') else 'gray'
            ttk.Label(guide_frame, text=line, 
                     font=('맑은 고딕', 9), foreground=fg_color).pack(anchor=tk.W)
        
        # 버튼 영역
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(10, 10))
        
        ttk.Button(btn_frame, text="📥 양식 다운로드", style='Secondary.TButton',
                  command=self._download_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📂 리스트 불러오기", style='Secondary.TButton',
                  command=self._import_list).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🗑️ 전체 삭제", style='Secondary.TButton',
                  command=self._clear_batch_masks).pack(side=tk.LEFT)
        
        # 리스트 영역
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 리스트 헤더
        count_frame = ttk.Frame(list_frame)
        count_frame.pack(fill=tk.X)
        self.batch_count_var = tk.StringVar(value="불러온 항목: 0개")
        ttk.Label(count_frame, textvariable=self.batch_count_var,
                 font=('맑은 고딕', 9), foreground='#666666').pack(anchor=tk.W)
        
        # 리스트박스
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.batch_mask_listbox = tk.Listbox(listbox_frame, height=6,
                                             font=('맑은 고딕', 9),
                                             selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL,
                                 command=self.batch_mask_listbox.yview)
        self.batch_mask_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.batch_mask_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_action_section(self, parent):
        """실행 버튼 섹션 생성"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=15)
        
        # 중앙 정렬을 위한 내부 프레임
        center_frame = ttk.Frame(action_frame)
        center_frame.pack()
        
        self.start_btn = ttk.Button(center_frame, text="🔒 마스킹 시작",
                                   style='Action.TButton',
                                   command=self._start_processing)
        self.start_btn.pack()
        
        # 진행률 표시
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(action_frame, 
                                           variable=self.progress_var,
                                           maximum=100,
                                           length=400)
        self.progress_bar.pack(pady=(10, 0))
    
    def _create_log_section(self, parent):
        """로그 섹션 생성"""
        log_frame = ttk.LabelFrame(parent, text="📋 처리 로그", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8,
                                                  font=('Consolas', 9),
                                                  state='disabled',
                                                  wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _log(self, message: str):
        """로그 메시지 추가"""
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[LOG] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()
    
    def _log_success(self, message: str):
        """성공 메시지 로그"""
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[✓] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()
    
    def _log_error(self, message: str):
        """에러 메시지 로그"""
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[✗] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()
    
    # === 파일 선택 ===
    def _select_file(self):
        """PDF 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="PDF 파일 선택",
            filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
        )
        if file_path:
            self.pdf_path = file_path
            self.file_path_var.set(file_path)
            self._log(f"파일 선택됨: {os.path.basename(file_path)}")
    
    # === 직접 입력 마스킹 관리 ===
    def _add_direct_mask(self):
        """직접 입력한 마스킹 텍스트 추가"""
        text = self.direct_mask_entry.get().strip()
        
        if not text:
            messagebox.showwarning("경고", "마스킹할 텍스트를 입력해주세요.")
            return
        
        if text not in self.direct_mask_list:
            self.direct_mask_list.append(text)
            self.direct_mask_listbox.insert(tk.END, text)
            self._log(f"마스킹 텍스트 추가: '{text}'")
            self.direct_mask_entry.delete(0, tk.END)
        else:
            messagebox.showinfo("알림", "이미 추가된 텍스트입니다.")
    
    def _remove_direct_mask(self):
        """선택된 직접 입력 마스킹 텍스트 삭제"""
        selection = self.direct_mask_listbox.curselection()
        if selection:
            index = selection[0]
            removed = self.direct_mask_list.pop(index)
            self.direct_mask_listbox.delete(index)
            self._log(f"마스킹 텍스트 삭제: '{removed}'")
    
    def _clear_direct_masks(self):
        """직접 입력한 모든 마스킹 텍스트 삭제"""
        if self.direct_mask_list:
            if messagebox.askyesno("확인", "직접 입력한 모든 텍스트를 삭제하시겠습니까?"):
                self.direct_mask_list.clear()
                self.direct_mask_listbox.delete(0, tk.END)
                self._log("직접 입력한 모든 마스킹 텍스트가 삭제되었습니다.")
    
    # === 일괄 입력 마스킹 관리 ===
    def _clear_batch_masks(self):
        """일괄 입력한 모든 마스킹 텍스트 삭제"""
        if self.batch_mask_list:
            if messagebox.askyesno("확인", "불러온 모든 텍스트를 삭제하시겠습니까?"):
                self.batch_mask_list.clear()
                self.batch_mask_listbox.delete(0, tk.END)
                self.batch_count_var.set("불러온 항목: 0개")
                self._log("일괄 입력한 모든 마스킹 텍스트가 삭제되었습니다.")
    
    def _download_template(self):
        """CSV 양식 파일 다운로드"""
        file_path = filedialog.asksaveasfilename(
            title="양식 파일 저장",
            defaultextension=".csv",
            filetypes=[("CSV 파일", "*.csv")],
            initialfile="마스킹_텍스트_양식.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                # 헤더 작성
                writer.writerow(["마스킹할_텍스트", "비고(선택사항)"])
                # 예시 데이터
                writer.writerow(["홍길동", "이름 예시"])
                writer.writerow(["서울고등학교", "학교명 예시"])
                writer.writerow(["010-1234-5678", "전화번호 예시"])
            
            self._log_success(f"양식 파일 저장 완료: {file_path}")
            messagebox.showinfo("완료", f"양식 파일이 저장되었습니다.\n\n{file_path}\n\n첫 번째 열에 마스킹할 텍스트를 입력하세요.\n두 번째 열(비고)은 무시됩니다.")
            
        except Exception as e:
            self._log_error(f"양식 파일 저장 실패: {str(e)}")
            messagebox.showerror("오류", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def _import_list(self):
        """외부 파일에서 마스킹 리스트 불러오기"""
        file_path = filedialog.askopenfilename(
            title="리스트 파일 선택",
            filetypes=[
                ("CSV 파일", "*.csv"),
                ("텍스트 파일", "*.txt"),
                ("모든 파일", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            skipped_count = 0
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    for row_idx, row in enumerate(reader):
                        if row:
                            text = row[0].strip()
                            # 헤더 행 건너뛰기
                            if row_idx == 0 and ("마스킹" in text or "텍스트" in text or "이름" in text or "text" in text.lower()):
                                skipped_count += 1
                                continue
                            if text and text not in self.batch_mask_list:
                                self.batch_mask_list.append(text)
                                self.batch_mask_listbox.insert(tk.END, text)
                                imported_count += 1
            else:  # .txt 또는 기타
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    for line in f:
                        text = line.strip()
                        if text and text not in self.batch_mask_list:
                            self.batch_mask_list.append(text)
                            self.batch_mask_listbox.insert(tk.END, text)
                            imported_count += 1
            
            # 카운트 업데이트
            total_count = len(self.batch_mask_list)
            self.batch_count_var.set(f"불러온 항목: {total_count}개")
            
            msg = f"{imported_count}개의 텍스트가 추가되었습니다."
            if skipped_count > 0:
                msg += f"\n(헤더 {skipped_count}개 건너뜀)"
            
            self._log_success(f"리스트 불러오기 완료: {imported_count}개 항목 추가됨")
            messagebox.showinfo("완료", msg)
            
        except Exception as e:
            self._log_error(f"리스트 불러오기 실패: {str(e)}")
            messagebox.showerror("오류", f"파일을 읽는 중 오류가 발생했습니다:\n{str(e)}")
    
    # === PDF 처리 ===
    def _start_processing(self):
        """PDF 처리 시작"""
        # 유효성 검사
        if not self.pdf_path:
            messagebox.showwarning("경고", "PDF 파일을 선택해주세요.")
            return
        
        # 마스킹할 텍스트 합치기
        all_mask_texts = list(set(self.direct_mask_list + self.batch_mask_list))
        
        if not all_mask_texts:
            messagebox.showwarning("경고", "마스킹할 텍스트가 없습니다.\n직접 입력하거나 리스트를 불러와주세요.")
            return
        
        if not self.korean_font_path:
            result = messagebox.askyesno(
                "경고", 
                "한글 폰트를 찾을 수 없습니다.\n계속하시겠습니까?"
            )
            if not result:
                return
        
        # 버튼 비활성화
        self.start_btn.configure(state='disabled')
        self.progress_var.set(0)
        
        # 별도 스레드에서 처리
        thread = threading.Thread(target=self._process_pdf_thread, daemon=True)
        thread.start()
    
    def _get_page_rotation(self, page) -> int:
        """
        페이지의 회전 각도 반환
        Returns: 0, 90, 180, 270 중 하나
        """
        return page.rotation
    
    def _is_landscape_page(self, page) -> bool:
        """
        페이지가 가로 방향인지 확인
        Returns: True if landscape, False if portrait
        """
        rect = page.rect
        # 회전을 고려한 실제 방향 확인
        rotation = page.rotation
        
        if rotation in [90, 270]:
            # 90도 또는 270도 회전된 경우, 실제 보이는 방향이 반전됨
            return rect.height > rect.width
        else:
            # 0도 또는 180도
            return rect.width > rect.height
    
    def _process_pdf_thread(self):
        """PDF 처리 스레드"""
        try:
            self._log("=" * 50)
            self._log("PDF 마스킹 처리를 시작합니다...")
            
            # 마스킹할 텍스트 합치기 (중복 제거)
            all_mask_texts = list(set(self.direct_mask_list + self.batch_mask_list))
            self._log(f"마스킹할 텍스트: {len(all_mask_texts)}개")
            
            # PDF 열기
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)
            self._log(f"총 {total_pages}페이지 처리 예정")
            
            # 처리 통계
            stats: Dict[str, int] = {}
            
            # 각 페이지 처리
            for page_num in range(total_pages):
                page = doc[page_num]
                rotation = self._get_page_rotation(page)
                is_landscape = self._is_landscape_page(page)
                
                self._log(f"페이지 {page_num + 1}/{total_pages} 처리 중... (회전: {rotation}°, {'가로' if is_landscape else '세로'}방향)")
                
                # 마스킹 처리
                for mask_text in all_mask_texts:
                    instances = page.search_for(mask_text)
                    if instances:
                        count = len(instances)
                        stats[mask_text] = stats.get(mask_text, 0) + count
                        
                        for rect in instances:
                            # 검정 박스로 마스킹 (텍스트 없음)
                            page.add_redact_annot(
                                rect,
                                text="",  # 텍스트 없음
                                fill=(0, 0, 0),  # 검정 배경
                            )
                
                # 리댁션 적용 (원본 데이터 완전 제거!)
                # 이 단계가 보안의 핵심 - 원본 텍스트가 PDF에서 완전히 삭제됨
                page.apply_redactions()
                
                # 진행률 업데이트
                progress = ((page_num + 1) / total_pages) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()
            
            # 결과 파일 저장
            output_path = self._generate_output_path()
            
            # garbage=4: 불필요한 객체 제거로 보안 강화
            # deflate=True: 압축
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            
            # 처리 완료 통계 출력
            self._log("=" * 50)
            self._log_success("PDF 처리가 완료되었습니다!")
            self._log(f"저장 위치: {output_path}")
            self._log("-" * 30)
            self._log("처리 통계:")
            
            for text, count in stats.items():
                self._log_success(f"  '{text}' : {count}건 처리됨")
            
            if not stats:
                self._log("  처리된 항목이 없습니다.")
            
            self._log("=" * 50)
            
            # 완료 메시지
            self.root.after(0, lambda: messagebox.showinfo(
                "완료",
                f"PDF 처리가 완료되었습니다!\n\n저장 위치:\n{output_path}"
            ))
            
        except Exception as e:
            self._log_error(f"오류 발생: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror(
                "오류",
                f"PDF 처리 중 오류가 발생했습니다:\n{str(e)}"
            ))
        
        finally:
            # 버튼 다시 활성화
            self.root.after(0, lambda: self.start_btn.configure(state='normal'))
            self.root.after(0, lambda: self.progress_var.set(100))
    
    def _generate_output_path(self) -> str:
        """출력 파일 경로 생성"""
        path = Path(self.pdf_path)
        output_name = f"{path.stem}_secure{path.suffix}"
        return str(path.parent / output_name)


def main():
    """메인 함수"""
    root = tk.Tk()
    
    # 고DPI 지원 (Windows)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    
    app = SecurePDFEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
