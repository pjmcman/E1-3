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


if __name__ == "__main__":
    # 2단계 확인용: 3×3 Cross 필터와 X 필터에 Cross 패턴을 넣어 본다.
    cross_filter = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]
    x_filter = [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
    ]
    cross_pattern = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]
    print("Cross 필터 점수:", mac(cross_pattern, cross_filter))
    print("X 필터 점수    :", mac(cross_pattern, x_filter))
