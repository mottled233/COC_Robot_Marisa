# COC_Robot_Marisa
一个提供各种COC跑团功能的聊天机器人，基于酷Q HTTP API。

支持的功能包括投骰子，录入属性和检定等。后续的开发会提供更多功能。
## 需求环境
**硬件**：一台服务器

**系统**：Ubuntu16.04，理论上支持各类linux系统

**软件**：
 - python 3.6 以上
 - Django
 -  Ubuntu Server 16.04 LTS & Docker CE 

## 配置docker
首先，在服务器上安装酷Q的docker以支持酷Q在Ubuntu系统上的运行。

参考连接：[酷Q on docker](https://cqp.cc/t/34558)

之前没接触过docker，这次算是碰了一鼻子灰。有理解错误的地方欢迎指正。

确定docker正确安装之后，使用以下命令来安装酷Q镜像：

```
docker pull coolq/wine-coolq
```
之后，在任意目录下新建一个文件夹，比如：

```
mkdir /root/coolq-data # 任意路径均可
```
运行docker镜像
```
docker run --name=coolq --rm -p 8080:9000 -p 5700:5700 -v /root/coolq-data:/home/user/coolq -e VNC_PASSWD=12345678 -e COOLQ_ACCOUNT=123456 coolq/wine-coolq
```
其中，--rm可以换成-d，就可以以服务的形式在后台运行，并使用以下命令控制：

```
docker start coolq # 启动
docker stop coolq # 终止
docker logs coolq # 查看
```
另外的可以修改的参数包括：
参数|值

---------|-------------

 -p 8080:9000 |可以把8080改到任意端口，用于使用浏览器连接docker的桌面。
 
 -p 5700:5700 |可以把前一个5700改成任意端口，用于连接酷Q的HTTP API。
 
 -v /root/coolq-data|可以改成之前新建的文件夹，用于做文件夹储存位置的映射
 
 VNC_PASSWD=12345678|可以自己设置密码，用于连接docker的远程桌面
 
 COOLQ_ACCOUNT=123456|登录的机器人的QQ号
 
运行后，会看到控制台中输出一系列日志。当你看到 [CQDaemon] Started CoolQ . 时，说明已启动成功。

此时，在浏览器中访问 http://你的服务器IP:你的端口 即可看到远程操作登录页面，输入密码，看到 酷Q Air 登录界面即为成功。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200214110518879.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L21vdHRsZWQyMzM=,size_16,color_FFFFFF,t_70)
此时，在新建的文件夹下会多出酷Q的相关文件，文件结构和在windows平台一样。在app文件夹下可以放入cpk文件添加插件。

## 配置HTTP API
酷Q HTTP API，以酷Q的一个插件形式存在，[下载地址](https://github.com/richardchien/coolq-http-api/releases)
基本上，它在启动后会自动搭建一个HTTP服务器，向其发送标准HTTP形式的请求命令即可实现对酷Q的调用。同时，酷Q接收到的信息会通过它转发到配置的地址，这样就避免了复杂的酷Q的开发。之前也试过使用python api，但是由于在服务器上酷Q是运行在docker里，给docker里再装一个python这太麻烦了。

下载好io.github.richardchien.coolqhttpapi.cpk文件后，将其放在之前建的酷Q文件夹下的app文件夹下，这时可以在远程桌面上的酷Q悬浮窗上单击右键，点击应用管理，重载应用后即可看到有HTTP API的插件。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200214110657371.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L21vdHRsZWQyMzM=,size_16,color_FFFFFF,t_70)
点击该插件，点击启用，会弹出一个命令行窗口记录日志，不要关闭该窗口。

在`{酷Q文件夹}/data/app`下面，会生成一个`io.github.richardchien.coolqhttpapi`文件夹，其中会生成`config/{登录QQ}.json`文件。

打开对其配置，在`"post_url": ""`一项中，填入上报的服务器的地址即可实现对酷Q接收到的信息的转发，转发会以HTTP Post的形式发送，具体格式参照下面的资料和下一节。

此时HTTP API安装完成，参考如下资料来对API进行学习和测试：[HTTP API](https://richardchien.gitee.io/coolq-http-api/docs/4.12/#/API)

## 搭建处理服务器
现在酷Q提供了一个HTTP的接口供调用了，那么我们就可以搭建一个用于处理具体逻辑的服务器，来处理酷Q的信息了。

在这里我选用的是python的Django框架，当然其他语言的其他框架都是可以的。关于框架的使用，不在这里详述。

下载本项目代码后，在项目目录下使用命令：
```
python manage.py runserver 0.0.0.0:8000
```
即可启动处理服务器。

## 命令与功能
命令指以`/`开头的信息，使用`help`查看当前支持的命令。
