# xor cipher

搜索 `xor cipher` ，可知是异或密码，推测 flag 可能为 key。

安装 xortool 然后在猜测原文为英语正常文段的情况下猜测 key：

```
> xortool cipher.txt -c ' '
The most probable key lengths:
   2:   11.1%
   4:   10.3%
   6:   10.2%
  10:   8.7%
  13:   17.1%
  16:   7.2%
  20:   6.0%
  26:   15.8%
  39:   6.6%
  52:   7.1%
Key-length can be 4*n
4 possible key(s) of length 13:
_etCr\x03sx!e_q8
_etCr\x03sx!}_q8
_HtCr\x03sx!e_q8
_HtCr\x03sx!}_q8
Found 0 plaintexts with 95.0%+ valid characters
```

尝试了会 length=13，但是并没有找到一个看起来像 key 的解。于是开始尝试 length=26：

```
> xortool cipher.txt -c ' ' -l 26
16 possible key(s) of length 26:
THUC\x1d\x03{x!3_es_eter s1&enq8
THUC\x1d\x03{x!3_es_eter s=&enq8
THUC\x1d\x03{x!3_es_eteres1&enq8
THUC\x1d\x03{x!3_es_eteres=&enq8
THUC\x1d\x03{x!3_e6_eter s1&enq8
...
Found 16 plaintexts with 95.0%+ valid characters
```

前缀 `THUC` 表明 length 极大概率为 26.

由于 key 是循环使用，所以一个 key 位会同时对应多处原文，对于 key 前缀我们已经知道是 `THUCTF{`，故可以确定连续 7 位的原文，接着便可以通过观察转化后的原文来依次推测每个 key 位的字符，最后得到 key.