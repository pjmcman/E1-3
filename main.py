"""Mini NPU 시뮬레이터 - MAC 연산으로 Cross/X 패턴을 판정한다."""

import json
import time

# 두 점수의 차이가 이 값보다 작으면 동점으로 본다 (부동소수점 오차 대비).
EPSILON = 1e-9

# 성능 측정 시 MAC 연산을 반복하는 횟수
REPEAT = 10

# 모드 2에서 읽을 데이터 파일
DATA_FILE = "data.json"

# 여러 표기의 라벨을 표준 라벨("Cross", "X")로 맞추는 표
# (소문자로 바꾼 뒤 찾으므로 "CROSS", "Cross", "X"도 처리된다)
LABEL_ALIASES = {
    "+": "Cross",
    "cross": "Cross",
    "x": "X",
}


def mac(pattern, filter_):
    """같은 크기의 2차원 리스트 두 개를 MAC(Multiply-Accumulate) 연산한다.

    같은 위치(i, j)의 값끼리 곱한 뒤 모두 더한 값을 돌려준다.
    N×N 크기라면 곱셈과 덧셈을 N² 번 하므로 시간 복잡도는 O(N²)이다.
    크기가 다르면 ValueError를 발생시킨다.
    """
    if len(pattern) != len(filter_):
        raise ValueError(
            f"행 수가 다릅니다: 패턴 {len(pattern)}행, 필터 {len(filter_)}행"
        )

    total = 0.0
    for i in range(len(pattern)):
        if len(pattern[i]) != len(filter_[i]):
            raise ValueError(
                f"{i + 1}행의 열 수가 다릅니다: "
                f"패턴 {len(pattern[i])}열, 필터 {len(filter_[i])}열"
            )
        for j in range(len(pattern[i])):
            total += pattern[i][j] * filter_[i][j]
    return total


def parse_row(line, size):
    """공백으로 구분된 한 줄을 숫자 리스트로 바꾼다.

    칸 수가 size와 다르거나 숫자가 아닌 값이 있으면 ValueError를 발생시킨다.
    """
    tokens = line.split()
    if len(tokens) != size:
        raise ValueError(f"입력된 숫자 {len(tokens)}개")

    row = []
    for token in tokens:
        try:
            row.append(float(token))
        except ValueError:
            raise ValueError(f"'{token}'은(는) 숫자가 아님") from None
    return row


def input_matrix(name, size=3):
    """size×size 행렬을 한 줄씩 입력받는다.

    잘못 입력한 줄은 오류 이유를 보여 주고 그 줄만 다시 입력받는다.
    """
    print(f"\n[{name}] {size}×{size} 행렬을 한 줄에 {size}개씩, 공백으로 구분해 입력하세요.")
    matrix = []
    while len(matrix) < size:
        line = input(f"  {len(matrix) + 1}행> ")
        try:
            matrix.append(parse_row(line, size))
        except ValueError as error:
            print(
                f"  입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요. "
                f"({error}) {len(matrix) + 1}행을 다시 입력하세요."
            )
    return matrix


def print_matrix(name, matrix):
    """행렬을 보기 좋게 출력한다."""
    print(f"[{name}]")
    for row in matrix:
        print("  " + " ".join(f"{value:g}" for value in row))


def judge(score_1, score_2, label_1, label_2, tie_label):
    """두 점수를 epsilon 기준으로 비교해 더 큰 쪽의 라벨을 돌려준다.

    차이가 EPSILON보다 작으면 동점으로 보고 tie_label을 돌려준다.
    """
    if abs(score_1 - score_2) < EPSILON:
        return tie_label
    if score_1 > score_2:
        return label_1
    return label_2


def measure_mac_ms(pattern, filter_, repeat=REPEAT):
    """MAC 연산을 repeat번 반복해 1회 평균 시간(ms)을 돌려준다.

    입출력 시간은 빼고 mac() 호출 구간만 잰다.
    """
    start = time.perf_counter()
    for _ in range(repeat):
        mac(pattern, filter_)
    elapsed = time.perf_counter() - start
    return elapsed / repeat * 1000


def print_section(number, title):
    """출력 구역 제목을 출력한다."""
    print("\n#" + "-" * 40)
    print(f"# [{number}] {title}")
    print("#" + "-" * 40)


def print_performance_table(rows):
    """크기별 성능 표를 출력한다. rows는 (N, 평균 ms) 목록이다."""
    # 한글은 화면에서 2칸을 차지하므로 제목 줄은 칸 수를 직접 맞춘다.
    print("크기      " + "   평균 시간(ms)" + "   연산 횟수(N²)")
    print("-" * 42)
    for size, avg_ms in rows:
        print(f"{f'{size}x{size}':<10}{avg_ms:>16.4f}{size * size:>16}")


def run_user_mode():
    """모드 1: 3×3 필터 A, B와 패턴을 입력받아 판정한다."""
    print_section(1, "필터 입력")
    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")

    print("\n필터 저장 확인")
    print_matrix("필터 A", filter_a)
    print_matrix("필터 B", filter_b)

    print_section(2, "패턴 입력")
    pattern = input_matrix("패턴")
    print("\n패턴 저장 확인")
    print_matrix("패턴", pattern)

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    # 필터 A, B를 각각 REPEAT번 재고, MAC 1회 평균을 구한다.
    avg_ms = (measure_mac_ms(pattern, filter_a) + measure_mac_ms(pattern, filter_b)) / 2
    result = judge(score_a, score_b, "A", "B", "판정 불가")

    print_section(3, "MAC 결과")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(MAC 1회, 평균/{REPEAT}회): {avg_ms:.4f} ms")
    if result == "판정 불가":
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    else:
        print(f"판정: {result}")

    print_section(4, f"성능 분석 (평균/{REPEAT}회)")
    print_performance_table([(3, avg_ms)])


def normalize_label(raw):
    """'+', 'cross', 'x' 같은 라벨을 표준 라벨 'Cross' 또는 'X'로 바꾼다.

    알 수 없는 라벨이면 ValueError를 발생시킨다.
    """
    key = str(raw).strip().lower()
    if key not in LABEL_ALIASES:
        raise ValueError(f"알 수 없는 라벨: {raw!r}")
    return LABEL_ALIASES[key]


def parse_size(key):
    """'size_5' 또는 'size_5_1' 형태의 키에서 크기 N(정수)을 꺼낸다."""
    parts = key.split("_")
    if len(parts) < 2 or parts[0] != "size" or not parts[1].isdigit():
        raise ValueError(f"키 형식이 'size_N'이 아님: {key!r}")
    return int(parts[1])


def load_data(path=DATA_FILE):
    """data.json을 읽어 (필터, 케이스 목록, 경고 목록)을 돌려준다.

    - 필터: {N: {"Cross": 행렬, "X": 행렬}}  (라벨은 표준 라벨로 정규화)
    - 케이스: [{"name", "size", "input", "expected"}, ...]  (expected도 정규화)
    - 경고: 읽다가 건너뛴 항목의 이유 문자열 목록

    파일이 없거나 JSON 형식이 아니면 OSError / json.JSONDecodeError가 그대로 올라간다.
    """
    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    warnings = []

    filters = {}
    for key, group in data.get("filters", {}).items():
        try:
            size = parse_size(key)
            filters[size] = {normalize_label(label): matrix for label, matrix in group.items()}
        except (ValueError, AttributeError) as error:
            warnings.append(f"필터 {key}: {error}")

    cases = []
    for name, case in data.get("patterns", {}).items():
        try:
            cases.append({
                "name": name,
                "size": parse_size(name),
                "input": case["input"],
                "expected": normalize_label(case["expected"]),
            })
        except (ValueError, KeyError, TypeError) as error:
            warnings.append(f"패턴 {name}: {error}")

    return filters, cases, warnings


def run_json_mode():
    """모드 2: data.json의 필터와 패턴을 읽고 라벨을 정규화한다.

    케이스별 판정은 6단계에서 추가한다.
    """
    print_section(1, "필터 로드")
    try:
        filters, cases, warnings = load_data()
    except OSError as error:
        print(f"{DATA_FILE} 파일을 열 수 없습니다: {error}")
        return
    except json.JSONDecodeError as error:
        print(f"{DATA_FILE}이(가) 올바른 JSON 형식이 아닙니다: {error}")
        return

    for size in sorted(filters):
        labels = ", ".join(sorted(filters[size]))
        print(f"✓ size_{size} 필터 로드 완료 ({labels})")
    for warning in warnings:
        print(f"⚠ {warning} (건너뜀)")

    print_section(2, "패턴 목록 (라벨 정규화)")
    for case in cases:
        print(f"{case['name']:<12} {case['size']:>2}x{case['size']:<3} expected: {case['expected']}")
    print(f"\n총 {len(cases)}개 패턴을 읽었습니다.")


def choose_mode():
    """모드 번호를 입력받는다. 1 또는 2가 아니면 다시 입력받는다."""
    print("\n[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    while True:
        choice = input("선택: ").strip()
        if choice in ("1", "2"):
            return choice
        print("1 또는 2를 입력하세요.")


def main():
    print("=== Mini NPU Simulator ===")
    try:
        if choose_mode() == "1":
            run_user_mode()
        else:
            run_json_mode()
    except (EOFError, KeyboardInterrupt):
        print("\n입력이 중단되어 프로그램을 종료합니다.")


if __name__ == "__main__":
    main()
