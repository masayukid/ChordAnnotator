![chordannotator_0](https://github.com/user-attachments/assets/faa0d049-7a1e-40de-b8a2-f96eb2ca343c)

# ChordAnnotator

楽曲の和音進行分析をサポートするアプリケーションです。音声ファイルを読み込むとスペクトログラムが表示され、顕著なピッチを選択するだけで自動で和音名がラベリングされます。
自動和音認識分野におけるデータセット不足の解消を目的として開発したもので、ルールベースの和音名推定により、音楽知識がないユーザーでもデータセットを作成できます。
また、ユーザーによる和音名の表記揺れ（Caug = C+, G7(9) = G9, ...）問題を解決しています。

## Demo

※著作権の関係で音声をオフにしています。

https://github.com/user-attachments/assets/6070ba54-b6a3-4305-8271-0496170b8254

## Requirement

- `flet==0.15.0`
- `keyboard==0.13.5`
- `librosa==0.10.1`
- `matplotlib==3.8.0`
- `Pillow==10.0.1`
- `pydub==0.25.1`
- `pygame==2.5.2`

## Usage

```
$ pip install -r requirements.txt
$ python app.py
```

### UserGuide
![操作方法](https://github.com/user-attachments/assets/62d58d29-70dc-422e-8c69-a3685fa09ce4)

## DataFormat

データは次のような形式で保存されます。

- metadata
  - duration : 音声ファイルの総再生時間 [s]
- content
  - time_stamp : 和音の開始時刻 [s]
  - key_name : キー名
  - chord_name : 和音名
  - pitch_row_hex : ピッチの選択状態

### ピッチの選択状態

ピッチの選択状態は、計88音階の選択状態を高音部から0（未選択）と1（選択中）で表したものを16進数に変換し、文字列として保存しています。
例えば、[C4, G3, E3, C3, G2, C2, C1] のように選択した場合、ピッチの状態は「0000000000000000000000000000000000000000000000001000010010001000010000001000000000001000」のような88桁の2進数で表され、冗長なゼロを除去して16進数に変換した「0x8488408008」という文字列で保存されます。

以下はデータの一例です。

```
{
    "metadata": {
        "duration": 25.443
    },
    "content": [
        {
            "time_stamp": 0.0,
            "key_name": "C/Am",
            "chord_name": "N.C.",
            "pitch_row_hex": "0x0"
        },
        {
            "time_stamp": 2.8665547325102874,
            "key_name": "C/Am",
            "chord_name": "C",
            "pitch_row_hex": "0x8488408008"
        },
        {
            "time_stamp": 5.712999999999999,
            "key_name": "C/Am",
            "chord_name": "Am",
            "pitch_row_hex": "0x1089081000"
        },

        ...,

        {
            "time_stamp": 22.704000000000004,
            "key_name": "C/Am",
            "chord_name": "G",
            "pitch_row_hex": "0x424420400"
        }
    ]
}
```

## License

[MIT license](https://en.wikipedia.org/wiki/MIT_License)
