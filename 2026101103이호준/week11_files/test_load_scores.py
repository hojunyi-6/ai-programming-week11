import csv
from pathlib import Path

import pytest
from load_scores import load_scores
from helpers import 쓰기


# 배포된 CSV와 같은 헤더로 테스트용 파일을 만듭니다.
def 파일만들기(tmp_path, 내용):
    헤더 = Path("scores.csv").read_text(
        encoding="utf-8-sig"
    ).splitlines()[0]

    경로 = tmp_path / "테스트.csv"
    경로.write_text(
        헤더 + "\n" + 내용,
        encoding="utf-8-sig"
    )
    return str(경로)


# ① 정상 파일: 학생 5명, 제외 0개
def test_01_normal():
    kept, skipped = load_scores("scores.csv")
    assert len(kept) == 5
    assert skipped == []


# ② 빈 줄: 학생 데이터만 읽기
def test_02_blank_lines(tmp_path):
    경로 = 파일만들기(
        tmp_path,
        "김하나,88\n\n이둘,90\n\n"
    )
    kept, skipped = load_scores(경로)
    assert kept == [("김하나", 88), ("이둘", 90)]
    assert skipped == []


# ③ 이름 속 쉼표: 이름 하나로 읽기
def test_03_comma_in_name(tmp_path):
    경로 = 파일만들기(
        tmp_path,
        '"김, 하나",88\n'
    )
    kept, skipped = load_scores(경로)
    assert kept == [("김, 하나", 88)]
    assert skipped == []


# ④ 없는 파일: 정해진 오류가 발생해야 통과
def test_04_missing_file(tmp_path):
    경로 = str(tmp_path / "없는파일.csv")
    with pytest.raises(FileNotFoundError):
        load_scores(경로)


# ⑤ 헤더만 있는 파일: 두 목록 모두 비어 있음
def test_05_header_only():
    kept, skipped = load_scores("empty.csv")
    assert kept == []
    assert skipped == []


# ⑥ 0점: 유효
def test_06_score_zero(tmp_path):
    경로 = str(tmp_path / "점수0.csv")
    쓰기(경로, 0)
    kept, skipped = load_scores(경로)
    assert len(kept) == 1
    assert kept[0][1] == 0
    assert skipped == []


# ⑦ 100점: 유효
def test_07_score_hundred(tmp_path):
    경로 = str(tmp_path / "점수100.csv")
    쓰기(경로, 100)
    kept, skipped = load_scores(경로)
    assert len(kept) == 1
    assert kept[0][1] == 100
    assert skipped == []


# ⑧ 101점: 무효이므로 제외 기록
def test_08_score_over(tmp_path):
    경로 = str(tmp_path / "점수101.csv")
    쓰기(경로, 101)
    kept, skipped = load_scores(경로)
    assert kept == []
    assert len(skipped) == 1