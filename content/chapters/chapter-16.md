<!-- Generated from ../source-html/chapter-16.html; do not edit independently. -->

# AI 健身教练：跟着视频练，让 AI 指出动作不标准的地方

健身很容易出现动作不标准的情况，如果没有教练指导，AI 能顶替教练吗？

如果把跟练过程录下来，能不能让 AI 先帮我们找出明显的差别？这一章会沿着这个思路做一个 AI 健身教练的示例。

<p></p>

先从视频里找出肩、肘、髋、膝等人体关键点，把动作变成可以比较的数据；再结合关节角度和动作发生的时间，找出学生与教练示范之间的差异。最后将这些结果和对应画面一起交给多模态模型，尝试生成更容易理解的反馈。

<p></p>

<a id="c16-s1"></a>

## 先在视频里找出肩、肘、髋、膝的位置

分析健身动作的第一步，是让计算机能够识别人体在视频中的姿态。视频本质上由连续的图像组成。对于计算机来说，原始图像也只是像素，并不知道画面中的肩膀、膝盖或者脚踝分别位于什么位置，所以我们首先使用人体姿态估计（Human Pose Estimation）技术，从每一帧图像中识别人体的主要位置。

本节实验使用 MediaPipe Pose 进行人体姿态识别。MediaPipe Pose 可以检测人体的 33 个关键点，包括肩部、肘部、手腕、髋部、膝盖和脚踝等位置。

![正文配图](<../../assets/manuscript-20260914/c16-d01e3ff2d01c12.webp>)

本次实验还是在 ModelScope 中的 Notebook 进行实验，实现要从视频中抽取关键点.

1\) 如果是直接运行代码的话，可能会报错 OSError: libEGL.so.1: cannot open shared object file: No such file or directory，所以这个步骤，我们需要先安装一些包

```text
apt-get install -y libegl1 libgl1 libgles2 libglib2.0-0 libsm6 libxext6 libxrender1
```

安装完成后提示：

![正文配图](<../../assets/manuscript-20260914/c16-291413e81f782e.webp>)

2）抽取关键点,代码如下：

```python
# -*- coding: utf-8 -*-

import cv2
import json
import argparse
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# 用于画骨骼图的连线 (只画主干，不画手指/脚趾细节，demo够用)
POSE_CONNECTIONS = [
    (11, 12),               # 双肩
    (11, 13), (13, 15),     # 左臂: 肩-肘-腕
    (12, 14), (14, 16),     # 右臂: 肩-肘-腕
    (11, 23), (12, 24),     # 肩到髋
    (23, 24),               # 双髋
    (23, 25), (25, 27),     # 左腿: 髋-膝-踝
    (24, 26), (26, 28),     # 右腿: 髋-膝-踝
    (27, 29), (28, 30),     # 踝-脚跟
    (27, 31), (28, 32),     # 踝-脚尖
]

def create_landmarker(model_path):
    """创建一个 PoseLandmarker 实例 (视频模式，逐帧按时间戳处理)"""
    base_options = mp_python.BaseOptions(model_asset_path=model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,                       # 每个画面只有一个人，设为1提高速度和准确率
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return vision.PoseLandmarker.create_from_options(options)

def detect(landmarker, frame_bgr, timestamp_ms):
    """对一帧图像做姿态检测，返回 33x4 的关键点列表 [x,y,z,visibility]，检测不到返回 None"""
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect_for_video(mp_image, timestamp_ms)
    if not result.pose_landmarks:
        return None
    lm = result.pose_landmarks[0]  # 取第一个人
    return [[p.x, p.y, p.z, p.visibility] for p in lm]

def draw_skeleton(frame, landmarks):
    """手动画骨骼线 (不依赖 mediapipe.solutions，因为部分新版本裁掉了这个模块)"""
    if landmarks is None:
        return frame
    h, w = frame.shape[:2]
    pts = [(int(p[0] * w), int(p[1] * h)) for p in landmarks]
    for i, j in POSE_CONNECTIONS:
        cv2.line(frame, pts[i], pts[j], (0, 255, 0), 2)
    for x, y in pts:
        cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)
    return frame

def main():

    video="/mnt/workspace/AIfitness/0912.mp4"
    model="/mnt/workspace/AIfitness/pose_landmarker_full.task"
    split=0.5
    out="/mnt/workspace/AIfitness/keypoints.json"  #"输出关键点json路径"
    debug_video="/mnt/workspace/AIfitness/debug_overlay.mp4"
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        raise RuntimeError(f"打不开视频: {video}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    split_x = int(w * split)

    print(f"视频信息: {w}x{h}, {fps:.1f}fps, 分割线 x={split_x}")

    landmarker_coach = create_landmarker(model)
    landmarker_student = create_landmarker(model)

    writer = cv2.VideoWriter(debug_video, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    frames_data = []
    frame_idx = 0
    detected_coach, detected_student = 0, 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp_ms = int(frame_idx * 1000 / fps)

        left = frame[:, :split_x].copy()
        right = frame[:, split_x:].copy()

        coach_lm = detect(landmarker_coach, left, timestamp_ms)
        student_lm = detect(landmarker_student, right, timestamp_ms)

        if coach_lm is not None:
            detected_coach += 1
        if student_lm is not None:
            detected_student += 1
        left_draw = draw_skeleton(left, coach_lm)
        right_draw = draw_skeleton(right, student_lm)
        writer.write(np.concatenate([left_draw, right_draw], axis=1))

        frames_data.append({
            "frame_idx": frame_idx,
            "timestamp_ms": timestamp_ms,
            "coach": coach_lm,
            "student": student_lm,
        })
        frame_idx += 1

        if frame_idx % 50 == 0:
            print(f"已处理 {frame_idx} 帧...")

    cap.release()
    writer.release()

    with open(out, "w", encoding="utf-8") as f:
        json.dump({
            "fps": fps, "width": w, "height": h, "split_x": split_x,
            "frames": frames_data,
        }, f)

    print(f"\n完成，共 {frame_idx} 帧")
    print(f"教练检测成功率: {detected_coach/frame_idx*100:.1f}%")
    print(f"学生检测成功率: {detected_student/frame_idx*100:.1f}%")

    
main()
```

经过姿态估计后，一帧普通的视频图像就可以转换成人体关键点数据，执行结果如下：

![正文配图](<../../assets/manuscript-20260914/c16-f064caa63bbfc5.webp>)

通过逐帧处理学生和教练的视频，可以得到连续的人体关键点序列。这样就把原本难以直接计算的视频内容，转换成了可以进一步分析的结构化数据。

<a id="c16-s2"></a>

## 人有高有矮，先把坐标尺度统一

得到人体关键点以后，还不能直接比较学生和教练的坐标。这是因为两个人的身高、身体比例以及距离摄像头的位置可能不同。即使完成完全相同的动作，关键点在画面中的坐标也可能存在明显差异。

因此，在比较人体姿态之前，可以先对关键点进行归一化处理。本节采用一种比较直接的方法：以左右髋部的中点作为人体的相对原点，再使用肩部中心到髋部中心的距离作为躯干长度，对人体尺度进行统一。归一化过程可以表示为：



```math
\mathbf{p}'_i=
\frac{\mathbf{p}_i-\mathbf{p}_{hip}}
{L_{torso}}
```



其中：

- $`\mathbf{p}_i`$ 表示原始关键点坐标；
- $`\mathbf{p}_{hip}`$ 表示左右髋部的中心位置；
- $`L_{torso}`$ 表示肩部中心到髋部中心的距离；
- $`\mathbf{p}'_i`$ 表示归一化后的关键点坐标。

对应代码如下：

```python
import numpy as np

LM = {
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_hip": 23,
    "right_hip": 24,
}

def normalize_landmarks(landmarks):
    pts = np.array([[p[0], p[1]] for p in landmarks], dtype=float)

    mid_hip = (
        pts[LM["left_hip"]] +
        pts[LM["right_hip"]]
    ) / 2

    mid_shoulder = (
        pts[LM["left_shoulder"]] +
        pts[LM["right_shoulder"]]
    ) / 2

    torso_len = np.linalg.norm(mid_shoulder - mid_hip)

    if torso_len < 1e-6:
        torso_len = 1e-6

    normed = (pts - mid_hip) / torso_len
    return normed
```

经过归一化以后，教练和学生的人体关键点会被转换到相对统一的坐标尺度中，后续比较更加关注身体姿态本身，而不是人在画面中的位置和大小。

<a id="c16-s3"></a>

## 动作有快有慢，要比较同一个阶段

除了人体大小不同，教练和学生完成动作的速度通常也不会完全一致。例如，教练已经到达深蹲最低点时，学生可能仍然处于下蹲过程中。如果简单地比较两段视频中的相同时间点，就可能把动作节奏不同误认为姿态不同。对于已经同步录制的视频，可以直接按照视频帧进行比较。如果教练和学生来自两段独立视频，则可以使用动态时间规整（Dynamic Time Warping，DTW）进行时间对齐。DTW 的基本思路是根据两段动作序列的变化寻找更加合理的对应关系。在具体实现中，可以先将每一帧的归一化人体关键点展开成一个向量，再计算教练帧和学生帧之间的距离：



```math
d(i,j)=\left\|
\mathbf{x}^{coach}_i-
\mathbf{x}^{student}_j
\right\|_2
```



其中：

$`\mathbf{x}^{coach}_i`$ 表示教练第 $`i`$ 帧的姿态特征；

$`\mathbf{x}^{student}_j`$ 表示学生第 $`j`$ 帧的姿态特征；

$`d(i,j)`$ 表示两帧姿态之间的距离。

DTW 再根据这些距离寻找一条累计代价较小的对齐路径，使动作节奏不同的两段视频能够进行对应比较。在本节实验中，教练和学生的视频已经同步录制，因此可以直接按帧进行比较，而不需要额外使用 DTW。

<a id="c16-s4"></a>

## 把动作差异算出来，看看关节角度差多少

完成关键点提取以后，就可以进一步根据人体关键点计算关节角度。例如，通过髋部、膝盖和脚踝三个关键点，可以计算膝关节角度；通过肩部、肘部和手腕三个关键点，可以计算肘关节角度。

设三个关键点分别为 $`A`$、$`B`$ 和 $`C`$，其中 $`B`$ 为需要计算角度的关节位置。先构造两个向量：$`\mathbf{u}=\mathbf{A}-\mathbf{B}`$，

$`\mathbf{v}=\mathbf{C}-\mathbf{B}`$,根据向量点积，可以得到两个向量之间的夹角：



```math
\theta=
\arccos
\left(
\frac{
\mathbf{u}\cdot\mathbf{v}
}{
\|\mathbf{u}\|
\|\mathbf{v}\|
}
\right)
```



代入三个关键点后，也可以写成：



```math
\theta=
\arccos
\left(
\frac{
(\mathbf{A}-\mathbf{B})\cdot(\mathbf{C}-\mathbf{B})
}{
\|\mathbf{A}-\mathbf{B}\|
\|\mathbf{C}-\mathbf{B}\|
}
\right)
```



例如，计算左膝角度时，$`A`$ 为左髋，$`B`$ 为左膝，$`C`$ 为左脚踝，最终得到的就是左膝位置处的夹角。本次实验主要关注左、右肘关节，左、右膝关节，左、右髋关节以及躯干前倾角。躯干前倾角通过肩部中心和髋部中心形成的连线，与竖直向上方向之间的夹角计算得到。

关节角度计算代码如下：

```python
import numpy as np

ANGLE_CN_NAME = {
    "left_elbow": "左肘",
    "right_elbow": "右肘",
    "left_knee": "左膝",
    "right_knee": "右膝",
    "left_hip": "左髋",
    "right_hip": "右髋",
    "trunk_tilt": "躯干前倾角",
}

ANGLE_DEFS = {
    "left_elbow":  ("left_shoulder", "left_elbow", "left_wrist"),
    "right_elbow": ("right_shoulder", "right_elbow", "right_wrist"),
    "left_knee":   ("left_hip", "left_knee", "left_ankle"),
    "right_knee":  ("right_hip", "right_knee", "right_ankle"),
    "left_hip":    ("left_shoulder", "left_hip", "left_knee"),
    "right_hip":   ("right_shoulder", "right_hip", "right_knee"),
}

LM = {
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
}

def calculate_angle(a, b, c):
    """计算B点处A-B-C三点形成的夹角，单位为度。"""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    ba = a - b
    bc = c - b

    cos_angle = np.dot(ba, bc) / (
        np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8
    )

    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    return float(
        np.degrees(np.arccos(cos_angle))
    )

def compute_all_angles(landmarks):
    """计算一帧中需要关注的全部关节角度。"""
    pts = [(p[0], p[1]) for p in landmarks]

    angles = {}

    for name, (a_name, b_name, c_name) in ANGLE_DEFS.items():
        a = pts[LM[a_name]]
        b = pts[LM[b_name]]
        c = pts[LM[c_name]]

        angles[name] = calculate_angle(a, b, c)

    # 计算躯干前倾角
    left_sh = pts[LM["left_shoulder"]]
    right_sh = pts[LM["right_shoulder"]]
    left_hip = pts[LM["left_hip"]]
    right_hip = pts[LM["right_hip"]]

    mid_sh = (
        (left_sh[0] + right_sh[0]) / 2,
        (left_sh[1] + right_sh[1]) / 2
    )

    mid_hip = (
        (left_hip[0] + right_hip[0]) / 2,
        (left_hip[1] + right_hip[1]) / 2
    )

    vertical_ref = (
        mid_hip[0],
        mid_hip[1] - 1.0
    )

    angles["trunk_tilt"] = calculate_angle(
        vertical_ref,
        mid_hip,
        mid_sh
    )

    return angles
```

得到学生和教练的关节角度后，可以计算两者之间的角度差异：

```math
\Delta\theta=
\left|
\theta_{student}
-
\theta_{coach}
\right|
```

，其中，$`\theta_{student}`$ 表示学生的关节角度，$`\theta_{coach}`$ 表示教练的关节角度，$`\Delta\theta`$ 表示两者之间的角度偏差。

人体关键点检测可能会存在轻微抖动。如果仅根据某一帧判断动作是否存在明显差异，容易受到偶然误差影响。因此，本节实验还会对角度差序列进行平滑处理。以长度为 $`w`$ 的滑动窗口为例，可以表示为：



```math
\overline{\Delta\theta}_t=
\frac{1}{w}
\sum_{k=0}^{w-1}
\Delta\theta_{t-k}
```



其中，$`\overline{\Delta\theta}_t`$ 表示平滑后的角度差。随后设置偏差阈值：

```math
\overline{\Delta\theta}_t>T
```

，$`T`$ 为设定的角度阈值。只有当角度差连续多帧超过阈值时，才将这一时间段标记为明显偏差，从而减少单帧抖动带来的误判。

对应的偏差分析代码如下：

```python
import numpy as np

DEVIATION_THRESHOLD_DEG = 15
MIN_DEVIATION_FRAMES = 6
SMOOTH_WINDOW = 5

def smooth(arr, window):
    if window <= 1:
        return arr

    kernel = np.ones(window) / window
    return np.convolve(arr, kernel, mode="same")

def find_deviation_segments(diff_arr, fps):

    segments = []
    in_seg = False
    start = 0
    for i, v in enumerate(diff_arr):
        if v > DEVIATION_THRESHOLD_DEG and not in_seg:
            in_seg = True
            start = i
        elif v <= DEVIATION_THRESHOLD_DEG and in_seg:
            in_seg = False
            if i - start >= MIN_DEVIATION_FRAMES:
                segments.append((start, i - 1))
    if in_seg and len(diff_arr) - start >= MIN_DEVIATION_FRAMES:
        segments.append((start, len(diff_arr) - 1))
    return segments
```

下面是核心代码主逻辑：

```python

def main():
  
    out_dir="/mnt/workspace/AIfitness/analysis"
    keypoints="/mnt/workspace/AIfitness/keypoints.json" 
    align=True

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "plots"), exist_ok=True)

    with open(keypoints, "r", encoding="utf-8") as f:
        data = json.load(f)
    fps = data["fps"]
    frames = data["frames"]

    coach_angles, coach_normed, coach_idx = build_angle_series(frames, "coach")
    student_angles, student_normed, student_idx = build_angle_series(frames, "student")

    print(f"教练有效帧数: {len(coach_idx)}, 学生有效帧数: {len(student_idx)}")

    n = min(len(coach_idx), len(student_idx))
    print(f"跳过DTW，按帧号直接对齐 (取前 {n} 个共同有效帧)")
    aligned_coach = {name: coach_angles[name][:n] for name in coach_angles}
    aligned_student = {name: student_angles[name][:n] for name in student_angles}
        

    report = {"joints": []}
    csv_lines = ["frame,joint,coach_angle,student_angle,diff"]

    for name in aligned_coach:
        coach_arr = np.array(aligned_coach[name])
        student_arr = np.array(aligned_student[name])
        n = min(len(coach_arr), len(student_arr))
        coach_arr, student_arr = coach_arr[:n], student_arr[:n]

        diff_raw = np.abs(coach_arr - student_arr)
        diff_smooth = smooth(diff_raw, SMOOTH_WINDOW)

        for i in range(n):
            csv_lines.append(f"{i},{name},{coach_arr[i]:.2f},{student_arr[i]:.2f},{diff_raw[i]:.2f}")

        segments = find_deviation_segments(diff_smooth, fps)
        cn_name = ANGLE_CN_NAME.get(name, name)
        for (s, e) in segments:
            report["joints"].append({
                "joint": name,
                "joint_cn": cn_name,
                "start_frame": int(s),
                "end_frame": int(e),
                "start_time_sec": round(s / fps, 2),
                "end_time_sec": round(e / fps, 2),
                "avg_diff_deg": round(float(np.mean(diff_smooth[s:e+1])), 1),
                "coach_avg_angle": round(float(np.mean(coach_arr[s:e+1])), 1),
                "student_avg_angle": round(float(np.mean(student_arr[s:e+1])), 1),
            })

        # 画对比曲线图
        plt.figure(figsize=(10, 4))
        t = np.arange(n) / fps
        plt.plot(t, coach_arr, label="教练", color="tab:blue", linewidth=1.5)
        plt.plot(t, student_arr, label="学生", color="tab:orange", linewidth=1.5)
        for (s, e) in segments:
            plt.axvspan(s / fps, e / fps, color="red", alpha=0.15)
        plt.title(f"{cn_name}角度对比 (红色区域=偏差超过{DEVIATION_THRESHOLD_DEG}度)")
        plt.xlabel("时间(秒)")
        plt.ylabel("角度(度)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "plots", f"{name}.png"), dpi=120)
        plt.close()

    with open(os.path.join(out_dir, "deviation_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "angles.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(csv_lines))

    print(f"\n完成，共发现 {len(report['joints'])} 处明显偏差片段")
    for item in report["joints"]:
        print(f"  [{item['start_time_sec']}s-{item['end_time_sec']}s] {item['joint_cn']}: "
              f"教练{item['coach_avg_angle']}° vs 学生{item['student_avg_angle']}° "
              f"(差{item['avg_diff_deg']}°)")
    print(f"\n详细报告 -> {out_dir}/deviation_report.json")
    print(f"角度对比图 -> {out_dir}/plots/")

if __name__ == "__main__":
    main()
```

执行代码结果如下：

![正文配图](<../../assets/manuscript-20260914/c16-4f12abaf6bef5f.webp>)

经过这一过程，可以得到每个明显偏差片段对应的关节、开始和结束位置、教练平均角度、学生平均角度以及平均角度差。这些结构化结果会在下一步与视频关键帧一起提供给多模态大模型。

<a id="c16-s5"></a>

## 有了角度和画面，让多模态模型解释差异

经过前面基于姿态估计的量化分析，已经能够得到学生动作在关键点、关节角度层面上与教练示范之间的具体差异。这些差异以数值形式呈现，精确但缺乏语义层面的理解，也难以直接转化为学员能够理解和执行的反馈建议。本节介绍如何在已有量化结果的基础上，引入多模态大模型完成动作语义理解与自然语言反馈生成，视频的信息如下：

[0912.mp4](<../../assets/manuscript-20260914/c16-b542ef5b332059.mp4>)

<a id="c16-s6"></a>

### 先分清做的是什么动作，再逐段分析

实际拍摄的健身跟练视频往往并非单一动作的持续重复，而是由多个不同动作依次组成，期间还可能穿插准备、休息、动作切换等过渡片段。如果不加区分，直接把整段视频的关键点数据和偏差结果一并交给大模型分析，会带来两方面问题：一是不同动作关注的关键关节和评价标准并不相同（例如深蹲重点关注膝、髋角度，弯举则重点关注肘部角度），混在一起容易造成评价标准相互干扰；二是让模型在同一次推理中同时完成"识别当前动作"与"评价动作质量"两项任务，会显著增加提示词的复杂度和模型的认知负担，对参数规模较小的模型尤其明显，容易导致输出质量下降。因此，在进行动作评价之前，本实验先对视频进行动作识别与分段，将其划分为若干相对独立、类型单一的动作片段，再针对每个片段分别展开后续分析。

本实验按固定时间间隔（如每隔 2 秒）从视频中抽取画面帧，只取教练侧画面输入多模态大模型判断当前画面属于哪一类动作（如"哑铃深蹲""哑铃弯举""侧平举""俯身划船"等），由于视觉分类本身存在一定的误判率，直接使用逐帧分类结果容易产生零散片段（例如连续动作中某一帧被偶然误判成其他类别）。为此，在得到连续帧的分类标签序列后，先做一次滑动窗口多数投票平滑，剔除孤立的误判帧；再将标签相同的连续帧合并为同一个动作片段；最后将时长过短的片段并入相邻片段，得到最终的分段结果。核心实现如下：

```python
import cv2
import json
import base64

import numpy as np
import requests

REPORT_PATH = "/mnt/workspace/AIfitness/analysis/deviation_report.json"  

KEYPOINTS_PATH = "/mnt/workspace/AIfitness/keypoints.json"
SEGMENTS_OUTPUT_PATH = "/mnt/workspace/AIfitness/segments.json"  
OUTPUT_PATH = "/mnt/workspace/AIfitness/analysis/feedback.md"
VLLM_BASE_URL = "http://127.0.0.1:8000"

SAMPLE_INTERVAL_SEC = 2.0        
MIN_SEGMENT_SEC = 4.0            
SMOOTH_WINDOW = 3               
MAX_IMAGES_PER_SEGMENT = 3      

CLASSIFY_PROMPT = (
    "这张图片是一个人在做健身动作的画面。请用2-6个字的中文简洁回答这是什么动作，"
    "例如：哑铃深蹲、哑铃弯举、侧平举、俯身划船、开合跳、休息/准备。"
    "只回答动作名称本身，不要任何其他文字、标点或解释。"
)

with open(KEYPOINTS_PATH, "r", encoding="utf-8") as f:
    SPLIT_X = json.load(f)["split_x"]
print(f"split_x = {SPLIT_X}")

resp = requests.get(f"{VLLM_BASE_URL}/v1/models", timeout=30)
resp.raise_for_status()
MODEL_NAME = resp.json()["data"][0]["id"]
print("当前 vLLM 模型：", MODEL_NAME)

def extract_coach_frame_b64(video_path, frame_idx, split_x, max_width=480):
    """分类只用教练那一侧的画面，教练动作标准、少遮挡，分类更准，还省token"""
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    coach = frame[:, :split_x].copy()
    h, w = coach.shape[:2]
    if w > max_width:
        scale = max_width / w
        coach = cv2.resize(coach, (max_width, int(h * scale)))
    ok, buf = cv2.imencode(".jpg", coach, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        return None
    return base64.b64encode(buf.tobytes()).decode("utf-8")
VIDEO_PATH = "/mnt/workspace/AIfitness/0912.mp4"

def classify_frame(img_b64):
    payload = {
        "model": MODEL_NAME,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": CLASSIFY_PROMPT},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + img_b64}},
            ],
        }],
        "temperature": 0.1,
        "max_tokens": 20,
    }
    resp = requests.post(f"{VLLM_BASE_URL}/v1/chat/completions", json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip().strip("。").strip()

def merge_labels_to_segments(samples, min_segment_sec, smooth_window):
    if not samples:
        return []
    labels = [l for _, l in samples]
    times = [t for t, _ in samples]
    n = len(labels)
    half = smooth_window // 2
    smoothed = [max(set(labels[max(0, i-half):min(n, i+half+1)]),
                     key=labels[max(0, i-half):min(n, i+half+1)].count) for i in range(n)]

    segs = []
    seg_start, seg_label = times[0], smoothed[0]
    for i in range(1, n):
        if smoothed[i] != seg_label:
            segs.append({"name": seg_label, "start_sec": seg_start, "end_sec": times[i]})
            seg_start, seg_label = times[i], smoothed[i]
    last_gap = (times[-1] - times[-2]) if n > 1 else SAMPLE_INTERVAL_SEC
    segs.append({"name": seg_label, "start_sec": seg_start, "end_sec": times[-1] + last_gap})

    merged = []
    for seg in segs:
        if merged and (seg["end_sec"] - seg["start_sec"]) < min_segment_sec:
            merged[-1]["end_sec"] = seg["end_sec"]
        else:
            merged.append(seg)
    return merged

def detect_segments():
    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    cap.release()
    print(f"\n视频时长 {duration:.1f}s，每 {SAMPLE_INTERVAL_SEC}s 抽一帧分类，"
          f"共约 {int(duration/SAMPLE_INTERVAL_SEC)} 次调用...")

    samples = []
    t = 0.0
    while t < duration:
        img_b64 = extract_coach_frame_b64(VIDEO_PATH, int(t * fps), SPLIT_X)
        if img_b64 is not None:
            label = classify_frame(img_b64)
            samples.append((t, label))
            print(f"  {t:6.1f}s -> {label}")
        t += SAMPLE_INTERVAL_SEC

    segments = merge_labels_to_segments(samples, MIN_SEGMENT_SEC, SMOOTH_WINDOW)
    print(f"\n识别出 {len(segments)} 个动作片段:")
    for seg in segments:
        print(f"  [{seg['start_sec']:.1f}s - {seg['end_sec']:.1f}s]  {seg['name']}")

    with open(SEGMENTS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    print(f"分段结果已保存 -> {SEGMENTS_OUTPUT_PATH}")
    return segments
segments = detect_segments()
```

首先需要在终端中启动 VLLM 程序，本实验采用 Qwen3-VL-2B-Instruct 模型，启动命令如下：

```text
vllm serve /mnt/workspace/models/Qwen3-VL-2B-Instruct \
--dtype bfloat16 \
--max_model_len 16384 \
--max-num-batched-tokens 16384
```

![正文配图](<../../assets/manuscript-20260914/c16-e6e0dfd5867dd4.webp>)

![正文配图](<../../assets/manuscript-20260914/c16-54a4ec9c354f48.webp>)

启动完成后，执行上面的代码，下面是执行结果：

![正文配图](<../../assets/manuscript-20260914/c16-da18e872515cf0.webp>)

<a id="c16-s7"></a>

### 把角度差异和画面对上，生成动作反馈

完成动作识别与分段后，系统已经知道视频中包含哪些动作，以及每个动作对应的时间范围。接下来需要将姿态分析得到的关节角度偏差与这些动作片段对应起来，并进一步转化为学员能够理解的动作评价和改进建议。

姿态分析得到的结果主要是关节角度、偏差大小以及偏差出现的时间等量化信息。这些数据能够说明学生与教练之间“差了多少”，但对于普通用户来说并不直观。本阶段按照动作分段对偏差数据进行重新组织，将属于同一动作的姿态偏差和关键帧组合在一起，再分别交给多模态大模型进行分析。在这一过程中，多模态大模型并不是直接根据视频重新判断动作是否标准，而是以姿态估计得到的量化结果作为主要依据，再结合关键帧观察动作幅度、身体姿态和稳定性等信息。例如，当系统已经检测到学生与教练在肘关节角度上存在明显差异时，大模型可以结合对应画面进一步解释这种差异在实际动作中的表现，并将角度数据转化为更加直观的训练建议。同时，评价过程按照动作片段分别进行。对于哑铃弯举、侧平举等不同动作，分别输入对应的偏差数据和关键帧，使模型每次只针对一个明确的动作进行分析。相比将整段视频中的多种动作一次性交给模型，这种方式能够减少不同动作之间的信息干扰，使生成的评价更加聚焦，下面是核心逻辑实现：

```python

def filter_deviations_by_segment(all_joints, seg_start, seg_end):
    """用偏差片段的中点时间判断这条偏差属于哪个动作分段"""
    return [d for d in all_joints
            if seg_start <= (d["start_time_sec"] + d["end_time_sec"]) / 2 < seg_end]

def extract_keyframe_b64(video_path, frame_idx, split_x, max_width=640):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    left = frame[:, :split_x].copy()
    right = frame[:, split_x:].copy()
    cv2.putText(left, "Coach", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(right, "Student", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    merged = np.concatenate([left, right], axis=1)
    h, w = merged.shape[:2]
    if w > max_width:
        scale = max_width / w
        merged = cv2.resize(merged, (max_width, int(h * scale)))
    ok, buf = cv2.imencode(".jpg", merged, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        return None
    return base64.b64encode(buf.tobytes()).decode("utf-8")

def build_prompt(exercise_name, deviations):
    if not deviations:
        return (f"这是一段学生跟随教练完成「{exercise_name}」的训练视频片段。"
                f"系统没有检测到明显的关节角度偏差，请给学生一句简短的鼓励和1个继续保持的建议。"
                f"直接输出点评内容。")
    lines = [
        f"这是一段学生跟随教练完成「{exercise_name}」的训练视频片段。",
        "", "系统已经通过人体姿态估计算法得到以下动作差异：", "",
    ]
    for i, d in enumerate(deviations, 1):
        lines.append(
            f"{i}. 时间 {d['start_time_sec']}s - {d['end_time_sec']}s，"
            f"{d['joint_cn']}：教练平均角度 {d['coach_avg_angle']}°，"
            f"学生平均角度 {d['student_avg_angle']}°，平均差值 {d['avg_diff_deg']}°。"
        )
    lines.extend([
        "", "同时提供了这些偏差时间点对应的视频截图。每张图片左侧是教练，右侧是学生。", "",
        "请结合关节角度数据和图片分析学生在这个动作里的表现。", "",
        "要求：",
        "1. 先总体评价这个动作完成情况。",
        "2. 再指出比较明显的差异，并给出改进建议。",
        "3. 优先参考已经计算出的关节角度数据，不要仅凭图片重新判断关节角度。",
        "4. 语言自然、简单，像健身教练给学生反馈，不要堆术语。",
        "5. 最后给出1个学生自己检查这个动作的小技巧。",
        "6. 不进行疾病、损伤等医学诊断。",
        "7. 直接输出点评内容，不要重复原始数据格式，不用再复述一遍是什么动作。",
    ])
    return "\n".join(lines)

def analyze_segment(name, deviations):
    print(f"\n--- 分析动作: {name}，匹配到偏差片段数: {len(deviations)} ---")
    top_deviations = sorted(deviations, key=lambda x: -x["avg_diff_deg"])[:MAX_IMAGES_PER_SEGMENT]

    content = [{"type": "text", "text": build_prompt(name, deviations)}]
    for i, d in enumerate(top_deviations, 1):
        mid_frame = (d["start_frame"] + d["end_frame"]) // 2
        img_b64 = extract_keyframe_b64(VIDEO_PATH, mid_frame, SPLIT_X)
        if img_b64 is None:
            continue
        content.append({"type": "text", "text": f"↑ 第{i}张：{d['joint_cn']}偏差画面"})
        content.append({"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + img_b64}})

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.3, "max_tokens": 800, "stream": False,
    }
    response = requests.post(f"{VLLM_BASE_URL}/v1/chat/completions", json=payload, timeout=300)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        print("vLLM 返回了错误，响应内容如下：")
        print(response.text[:2000])
        raise

    result = response.json()
    if "choices" not in result:
        print("vLLM 返回格式异常：", json.dumps(result, ensure_ascii=False)[:2000])
        raise RuntimeError("响应里没有 choices 字段")

    feedback = result["choices"][0]["message"]["content"]
    print(feedback[:200] + ("..." if len(feedback) > 200 else ""))
    return feedback

with open(REPORT_PATH, "r", encoding="utf-8") as f:
    flat_report = json.load(f)
all_joints = flat_report["joints"]
print(f"\nStep2原始偏差条数(整段视频): {len(all_joints)}")

md_parts = ["# AI健身教练分析报告\n"]
for seg in segments:
    matched = filter_deviations_by_segment(all_joints, seg["start_sec"], seg["end_sec"])
    feedback = analyze_segment(seg["name"], matched)
    md_parts.append(f"## {seg['name']} ({seg['start_sec']:.1f}s - {seg['end_sec']:.1f}s)\n")
    md_parts.append(feedback)
    md_parts.append("\n")

full_text = "\n".join(md_parts)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(full_text)

print("\n" + "=" * 60)
print(full_text)
print("=" * 60)
print(f"\n分析结果已保存：{OUTPUT_PATH}")
```

代码执行结果如下：

![正文配图](<../../assets/manuscript-20260914/c16-073624de36e98a.webp>)

我们也可以在生成的文档中看到模型对此次训练更加具体的总结反馈。

![正文配图](<../../assets/manuscript-20260914/c16-f19af53180de2d.webp>)

<a id="c16-s8"></a>

### 多记录几次，看看动作有没有变化

前面的动作识别、姿态分析和多模态评价，主要解决的是一次训练中动作完成得怎么样的问题。对于 AI 健身教练而言，如果进一步结合训练过程和历史数据，还可以从单次动作纠正扩展到更加连续的训练分析与个性化指导。可以将不同训练场次的数据进行保存和关联，形成长期训练记录。例如，持续记录同一动作的关节角度偏差、动作稳定性和完成情况，就可以比较学生经过多次训练后的变化。如果某项动作的偏差逐渐减小，说明动作掌握程度正在提高；如果某类问题长期存在，则可以在后续训练中持续提醒和重点关注。这样，AI 健身教练的分析对象就从一次训练扩展到了一个连续的训练过程。在此基础上，还可以进一步结合用户的训练目标和个人训练信息。例如，将增肌、减脂或体态改善等目标，以及训练频率、训练时长和历史训练情况与动作分析结果结合，大模型就可以生成更加符合个人情况的训练建议。AI 健身教练就不只是对某一个动作进行即时纠正，而是能够逐步形成从动作识别、姿态量化、动作评价到训练记录与个性化指导的完整应用流程。

<p></p>

以上所有实验步骤，可参考：https://modelscope.cn/gallery/liucong/bc955e19-cb4b-4029-bb0e-810eeaa166b4

<p></p>

<p></p>

<p></p>

<p></p>

<p></p>

<p></p>

<p></p>

<p></p>
