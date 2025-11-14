import streamlit as st
import streamlit.components.v1 as components
import random


def generate_rounds(count=10, max_attempts=20000):
    """Generate `count` rounds where all bases and targets are unique.

    Each round is a tuple (base, op, n, target). Both `base` and `target` are
    integers in 1..100 and no number appears in more than one round (neither as
    a base nor as a target).
    """
    ops = ["+", "-", "*", "/"]
    rounds = []
    used = set()
    attempts = 0
    while len(rounds) < count and attempts < max_attempts:
        attempts += 1
        b = random.randint(1, 100)
        if b in used:
            continue
        target = random.randint(1, 100)
        if target == b or target in used:
            continue

        found = False
        for op in random.sample(ops, k=len(ops)):
            if op == "+":
                n = target - b
                if 0 <= n <= 100:
                    rounds.append((b, op, n, target))
                    found = True
                    break
            elif op == "-":
                n = b - target
                if 0 <= n <= 100:
                    rounds.append((b, op, n, target))
                    found = True
                    break
            elif op == "*":
                if b != 0 and target % b == 0:
                    n = target // b
                    if 0 <= n <= 100:
                        rounds.append((b, op, n, target))
                        found = True
                        break
            else:  # division
                if target != 0 and b % target == 0:
                    n = b // target
                    if 1 <= n <= 100:
                        rounds.append((b, op, n, target))
                        found = True
                        break

        if found:
            used.add(b)
            used.add(target)

    if len(rounds) < count:
        raise RuntimeError("Unable to generate enough unique rounds; try again or increase max_attempts")

    return rounds


st.set_page_config(page_title="사칙연산으로 저울의 균형 맞추기 (Unique 10)", layout="centered")
st.title("⚖️ 사칙연산으로 저울의 균형 맞추기 — 10문항(중복 없음)")

st.markdown("학생은 오른쪽에 보이는 `기본숫자`에 연산기호와 숫자를 채워서 왼쪽에 보이는 목표값과 같아지도록 만들어야 합니다. 전체 10문항은 서로 다른 숫자(왼쪽/오른쪽 모두 중복 없음)를 사용합니다.")


if 'rounds' not in st.session_state:
    st.session_state.rounds = generate_rounds(10)
    st.session_state.current_idx = 0
    st.session_state.correct_count = 0
    st.session_state.solved_current = False
    st.session_state.message = ""


def load_current_round():
    b, op, n, target = st.session_state.rounds[st.session_state.current_idx]
    st.session_state.base = b
    st.session_state._solution_op = op
    st.session_state._solution_n = n
    st.session_state.target = target
    st.session_state.message = ""
    st.session_state.solved_current = False


def start_new_round():
    if st.session_state.current_idx < len(st.session_state.rounds) - 1:
        st.session_state.current_idx += 1
        load_current_round()


def reset_game():
    st.session_state.rounds = generate_rounds(10)
    st.session_state.current_idx = 0
    st.session_state.correct_count = 0
    st.session_state.solved_current = False
    st.session_state.message = ""
    load_current_round()


# ensure current round values loaded
if 'base' not in st.session_state:
    load_current_round()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("목표값 (왼쪽 저울)")
    st.markdown(f"<div style='font-size:48px; text-align:center;'>{st.session_state.target}</div>", unsafe_allow_html=True)

with col2:
    st.subheader("기본숫자 (오른쪽 저울)")
    st.markdown(f"<div style='font-size:48px; text-align:center;'>{st.session_state.base}</div>", unsafe_allow_html=True)
    st.write("빈칸을 채워 균형을 맞춰보세요:")
    op_input = st.selectbox("연산기호", ["+", "-", "*", "/"], index=0)
    n_input = st.number_input("숫자", min_value=0, max_value=100, value=1, step=1)

    if op_input == "/" and n_input == 0:
        st.warning("0으로 나눌 수 없습니다. 다른 숫자를 선택하세요.")

    # 계산된 학생의 값 (비교 및 시각화를 위해 실수 연산 사용)
    student_value = None
    try:
        n_val = int(n_input)
        if op_input == "+":
            student_value = float(st.session_state.base + n_val)
        elif op_input == "-":
            student_value = float(st.session_state.base - n_val)
        elif op_input == "*":
            student_value = float(st.session_state.base * n_val)
        else:
            if n_val == 0:
                student_value = None
            else:
                student_value = float(st.session_state.base) / float(n_val)
    except Exception:
        student_value = None

    # 시각화: student_value와 target의 차이에 따라 저울 기울기 각도 계산
    def compute_tilt_angle(left, right):
        if right is None:
            return 0
        diff = right - left  # 양수면 오른쪽이 더 무거움
        angle = diff * 2.0
        if angle > 25:
            angle = 25
        if angle < -25:
            angle = -25
        return angle

    angle = compute_tilt_angle(st.session_state.target, student_value)

    # SVG로 저울 렌더링
    left_label = st.session_state.target
    right_label = "?"
    if student_value is None:
        right_label = "—"
    else:
        # 값이 정수면 정수로, 아니면 소수 2자리로 표시
        right_label = int(student_value) if abs(student_value - int(student_value)) < 1e-9 else f"{student_value:.2f}"

    svg = f'''
    <svg width="420" height="220" viewBox="0 0 420 220" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.4"/>
        </filter>
      </defs>
      <g transform="translate(210,120)">
        <g transform="rotate({angle})">
          <rect x="-180" y="-8" width="360" height="16" rx="8" fill="#8B5E3C"/>
          <g id="left-pan" transform="translate(-120,20)">
            <circle cx="0" cy="0" r="28" fill="#f0f0f0" stroke="#ccc"/>
            <text x="0" y="6" font-size="16" text-anchor="middle" fill="#111">{left_label}</text>
          </g>
          <g id="right-pan" transform="translate(120,20)">
            <circle cx="0" cy="0" r="28" fill="#f8f8ff" stroke="#ccc"/>
            <text x="0" y="6" font-size="16" text-anchor="middle" fill="#111">{right_label}</text>
          </g>
        </g>
        <polygon points="-12,30 12,30 0,80" fill="#444"/>
        <rect x="-6" y="80" width="12" height="40" fill="#444"/>
      </g>
    </svg>
    '''

    components.html(svg, height=260)

    if st.button("정답 확인"):
        try:
            if student_value is None:
                st.session_state.message = "입력한 값으로 계산할 수 없습니다."
                st.error("유효한 숫자를 입력하세요.")
            else:
                if abs(student_value - float(st.session_state.target)) < 1e-9:
                    st.session_state.correct_count += 1
                    st.session_state.solved_current = True
                    st.success(f"정답! 현재 맞은 개수: {st.session_state.correct_count}/10")
                    st.session_state.message = f"정답: {st.session_state.base} {op_input} {int(n_input)} = {st.session_state.target}"
                    if st.session_state.correct_count >= 10:
                        st.balloons()
                        st.success("축하합니다! 10문제를 모두 맞혔습니다.")
                else:
                    st.session_state.message = f"틀렸습니다. 시도한 결과: {right_label}. 다시 시도해 보세요."
                    st.error("틀렸습니다. 다시 시도해 보세요.")
        except Exception as e:
            st.error(f"검사 중 오류가 발생했습니다: {e}")

st.write("---")
st.write(f"라운드: {st.session_state.current_idx + 1} / {len(st.session_state.rounds)} | 맞은 개수: {st.session_state.correct_count}/10")
if st.session_state.message:
    st.info(st.session_state.message)

cols = st.columns([1, 1, 1])
with cols[0]:
    if st.button("다시 시작"):
        reset_game()
with cols[1]:
    if st.session_state.solved_current and st.session_state.current_idx < len(st.session_state.rounds) - 1:
        if st.button("다음 문제로"):
            start_new_round()
with cols[2]:
    if st.session_state.current_idx == len(st.session_state.rounds) - 1 and st.session_state.solved_current:
        st.success("마지막 문제를 맞혔습니다! 게임을 다시 시작하거나 결과를 확인하세요.")

st.markdown("---")
st.caption("만든이: 학습용 예제 — 사칙연산 연습용 앱 (중복 없는 10문항)")
