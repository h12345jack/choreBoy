## part1
https://www.bilibili.com/ranking#!/all/0/1/7/

这个是B站热门视频排行榜
首先我需要把这个“综合”排行榜上100个视频的信息都抓下来
抓下来的数据结构大概这样    
![](./imgs/881508317096_.pic.jpg)

https://www.bilibili.com/index/rank/all-07-0.json

## part2
接下来就是，我需要每个视频的标签信息
![](./imgs/1061508317535_.pic_hd.jpg)
主要是作标签的内容分析，100个视频差不多就有七八百个标签了，人工分析差不多够了.标签的结构大概是这样
![](./imgs/1291508317877_.pic.jpg)

https://www.bilibili.com/video/av14534728/

https://api.bilibili.com/x/tag/archive/tags?aid=14534728&jsonp=jsonp

## part3
然后我还需要每个标签的修改记录
![](./imgs/1331508317934_.pic.jpg)
https://api.bilibili.com/x/tag/archive/log?&aid=14534728&pn=1&ps=20&jsonp=jsonp

## part4
然后我需要每个参与了标签修改的用户的信息
![](./imgs/1381508317989_.pic.jpg)




其他无关信息：
师姐，关于SP，在bilibili的sitemap里有大量的涉及。将其抽取出来可以发现。

http://www.bilibili.com/sitemap/sp.xml