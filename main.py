"""Mini NPU 시뮬레이터 - MAC 연산으로 Cross/X 패턴을 판정한다."""


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
        raise ValueError(f"숫자 {size}개가 필요합니다. (입력된 개수: {len(tokens)})")

    row = []
    for token in tokens:
        try:
            row.append(float(token))
        except ValueError:
            raise ValueError(f"'{token}'은(는) 숫자가 아닙니다.") from None
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
            print(f"  입력 오류: {error} {len(matrix) + 1}행을 다시 입력하세요.")
    return matrix


def print_matrix(name, matrix):
    """행렬을 보기 좋게 출력한다."""
    print(f"[{name}]")
    for row in matrix:
        print("  " + " ".join(f"{value:g}" for value in row))


if __name__ == "__main__":
    # 3단계 확인용: 필터 A, 필터 B, 패턴을 입력받아 그대로 출력해 본다.
    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")
    pattern = input_matrix("패턴")

    print("\n입력 확인")
    print_matrix("필터 A", filter_a)
    print_matrix("필터 B", filter_b)
    print_matrix("패턴", pattern)
