# txt2epub

---

**A python script convert Chinese novel text file to epub.**

## 2018-11-15

- 按照Epub3的规范，修改生成的epub的目录结构；
- 修改了章节目录的正则表达式，并增加了两种是否章节名的判断；
- 为Epub中增加了`stylesheet.css`文件，是适配我`KPW3`的`azw3`的样式表。
- 删除了原来的`zh2unicode`和`zh2utf8`函数，改为在`open`处指定编码；
