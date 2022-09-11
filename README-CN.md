# 这个Unciv服务端依赖于Python

这是一个简单的uncv服务端，使用内置于Python的http模块，类型为web服务器。

## 安装

1，请确保你已安装 Python3 .
2，这个Unciv服务端可以使用python 3.7\3.8\3.9 以及 3.10; 当然, 我们推荐 Python 3.9 和 3.10

使用 [git](https://git-scm.com) 来下载 服务端 Unciv_server

```bash
git clone https://github.com/Mape6/Unciv_server.git
cd Unciv_server
```

## 开服方法

```
用法: Unciv_server.py [-h] [-p PORT] [-g]
                       [-l {CRITICAL,ERROR,WARNING,INFO,DEBUG}]

这是一个简单的uncv HTTP Web服务器

可选指令:
  -h, --help            展示我们的 帮助 信息以及 exit
  
  -p PORT, --port PORT  指定服务器应侦听的端口
                        (默认为: 80)
                        
  -g, --game-logfiles   为每局游戏编写单独的日志文件
  
  -l {CRITICAL,ERROR,WARNING,INFO,DEBUG}, --log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
                        改变日志等级 (默认为: WARNING)
```

作者：此Web服务器不支持用于安全HTTPS连接的TLS。我建议在此Web服务器前面使用反向代理来处理证书和TLS会话。


## 贡献
欢迎拉取请求。对于重大更改，请先打开问题，讨论您想要更改的内容。


## 相关许可
此项目得到了 [MPL-2.0](https://github.com/Mape6/Unciv_server/blob/main/LICENSE) 的许可批准.
