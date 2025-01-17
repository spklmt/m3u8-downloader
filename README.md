# m3u8 下载器

> 简易 m3u8 下载器，仅供学习用途。

1. `catch.py`
   根据 `m3u8` 的 `url`，获取 `key` 解密 `ts` 文件并保存
2. `merge.py`
   将所有的 `ts` 文件合并成一个大的 `ts` 文件

3. 使用 `ffmpeg` 转化为 `mp4`

```cmd
ffmpeg -i merged.ts -c:v copy -c:a copy merged.mp4
```
