# 音频—时间轴契约

## 时间单位

- `fps` 是视频帧率，必须写入 `timeline.json`。
- 帧区间采用半开区间 `[start_frame, end_frame)`；结束帧不属于当前段或 cue。
- 所有由语言或配音触发的动作使用 `start_frame` / `end_frame`，不使用凭感觉估算的绝对秒数。
- 固定的视觉过渡时长只能作为命名的默认参数；它不能替代音频 cue。

## segments.json

```json
{
  "version": 1,
  "segments": [
    {
      "id": "seg-01",
      "chapter": "问题",
      "title": "核心问题",
      "text": "配音逐字原文"
    }
  ]
}
```

要求：`id` 唯一；`title` 和 `text` 非空；冻结后不在字幕或画面阶段改写 `text`。

## timeline.json

```json
{
  "version": 1,
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "duration_frames": 1800,
  "segments": [
    {
      "id": "seg-01",
      "start_frame": 0,
      "end_frame": 420,
      "cues": [
        {
          "id": "cue-01",
          "start_frame": 0,
          "end_frame": 180,
          "text": "配音逐字原文"
        }
      ]
    }
  ]
}
```

要求：

- `version`、`fps`、`duration_frames` 和 `segments` 必须存在。
- 段落按时间排序，区间不得反向或重叠；段落之间允许保留配音静音，但必须属于时间轴范围。
- cue 必须位于所属段落内，按时间排序且互不重叠。
- `duration_frames` 至少覆盖最后一个段落的 `end_frame`。
- `text` 与冻结稿对应句子一致；字幕不能另造一套文本。
- `width` 和 `height` 必须与目标画布一致；`fps` 不能在渲染工程里另行覆盖。

## 配音信号检查

在建立时间轴前检查：

1. 每段字数与实际时长没有明显异常。
2. 音频格式、声道和采样率统一。
3. 没有削波或异常长静音。
4. 拼接后的总时长与 cue 的最后结束时间一致。
5. 音频试听通过后才开始场景编码。

## 失败处理

时间轴校验失败时，先修复 `segments.json`、音频边界或 cue 数据，再渲染。画面层加补偿时间、另写一套字幕时钟或延后修复都属于表面修补。