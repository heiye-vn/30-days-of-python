# Linux 常用命令详解

> Linux 命令行不是要背一堆神秘咒语，而是学会用一组稳定的小工具完成日常工作：查看文件、移动目录、搜索内容、管理权限、观察进程、排查网络、压缩备份、查看磁盘和服务状态。本文按真实使用场景整理常用命令，并配上可以直接复制练习的例子。

---

## 一、命令行基础

### 1.1 命令的基本结构

Linux 命令通常由三部分组成：

```bash
命令 [选项] [参数]
```

例如：

```bash
ls -lh /var/log
```

含义是：

- `ls`：列出文件和目录。
- `-lh`：选项，`-l` 表示详细列表，`-h` 表示用更易读的单位显示大小。
- `/var/log`：参数，表示要查看的目录。

很多命令都支持短选项和长选项：

```bash
ls -a
ls --all
```

这两条都表示显示隐藏文件。

### 1.2 查看命令帮助

如果忘记命令怎么用，优先看帮助。

```bash
命令 --help
```

例如：

```bash
cp --help
```

查看更完整的手册：

```bash
man cp
```

在 `man` 页面中常用按键：

- `空格`：向下翻页。
- `b`：向上翻页。
- `/关键词`：搜索关键词。
- `n`：跳到下一个搜索结果。
- `q`：退出。

也可以用 `type` 或 `which` 查看命令来源：

```bash
type cd
which python3
```

`cd` 通常是 shell 内置命令，而 `python3` 多半是某个可执行文件路径。

---

## 二、目录与路径

### 2.1 pwd：查看当前目录

```bash
pwd
```

示例输出：

```text
/home/alice/project
```

当你不知道自己在哪个目录时，先执行 `pwd`。

### 2.2 cd：切换目录

进入指定目录：

```bash
cd /home/alice/project
```

回到用户主目录：

```bash
cd ~
```

或者直接：

```bash
cd
```

返回上一次所在目录：

```bash
cd -
```

进入上一级目录：

```bash
cd ..
```

进入上两级目录：

```bash
cd ../..
```

### 2.3 绝对路径与相对路径

绝对路径从根目录 `/` 开始：

```bash
cd /etc/nginx
```

相对路径从当前目录开始：

```bash
cd logs
cd ../data
```

如果当前目录是 `/home/alice/project`，那么：

```bash
cd logs
```

实际进入的是：

```text
/home/alice/project/logs
```

---

## 三、查看文件和目录

### 3.1 ls：列出目录内容

普通查看：

```bash
ls
```

查看详细信息：

```bash
ls -l
```

显示隐藏文件：

```bash
ls -a
```

详细信息加易读单位：

```bash
ls -lh
```

按修改时间排序：

```bash
ls -lt
```

按文件大小排序：

```bash
ls -lhS
```

查看某个目录：

```bash
ls -lh /var/log
```

`ls -l` 的输出示例：

```text
-rw-r--r-- 1 alice alice  128 Jul  5 10:20 README.md
drwxr-xr-x 2 alice alice 4096 Jul  5 10:21 src
```

第一列表示权限，开头是 `-` 表示普通文件，`d` 表示目录。

### 3.2 tree：树形查看目录

有些系统默认没有安装 `tree`，可以用包管理器安装。

```bash
tree
```

只显示两层：

```bash
tree -L 2
```

忽略某些目录：

```bash
tree -L 3 -I "node_modules|__pycache__|.git"
```

适合快速了解项目结构。

---

## 四、创建、复制、移动和删除

### 4.1 mkdir：创建目录

创建一个目录：

```bash
mkdir logs
```

一次创建多级目录：

```bash
mkdir -p data/raw/2026
```

`-p` 的好处是：中间目录不存在时自动创建，目录已存在时也不会报错。

### 4.2 touch：创建空文件或更新时间

创建空文件：

```bash
touch app.log
```

一次创建多个文件：

```bash
touch index.html style.css script.js
```

如果文件已存在，`touch` 会更新文件的修改时间。

### 4.3 cp：复制文件和目录

复制文件：

```bash
cp config.example.yml config.yml
```

复制到目录：

```bash
cp README.md docs/
```

复制目录：

```bash
cp -r src src_backup
```

保留权限、时间等信息：

```bash
cp -a project project_backup
```

复制前询问，避免覆盖：

```bash
cp -i app.conf /etc/app.conf
```

### 4.4 mv：移动或重命名

重命名文件：

```bash
mv old_name.txt new_name.txt
```

移动文件到目录：

```bash
mv app.log logs/
```

移动并改名：

```bash
mv logs/app.log logs/app-2026-07-05.log
```

移动前询问，避免覆盖：

```bash
mv -i config.yml config.yml.bak
```

### 4.5 rm：删除文件和目录

删除文件：

```bash
rm temp.txt
```

删除前询问：

```bash
rm -i temp.txt
```

删除空目录：

```bash
rmdir empty_dir
```

递归删除目录：

```bash
rm -r old_project
```

强制递归删除：

```bash
rm -rf old_project
```

`rm -rf` 很危险，执行前一定确认当前目录和目标路径：

```bash
pwd
ls -ld old_project
```

不要随手执行类似下面的命令：

```bash
rm -rf /
rm -rf /*
rm -rf $some_variable/*
```

变量为空或路径写错时，可能造成严重数据损坏。

---

## 五、查看文件内容

### 5.1 cat：一次性输出文件

```bash
cat README.md
```

显示行号：

```bash
cat -n README.md
```

适合查看较短文件，不适合大日志。

### 5.2 less：分页查看文件

```bash
less /var/log/syslog
```

常用按键：

- `空格`：下一页。
- `b`：上一页。
- `g`：回到开头。
- `G`：跳到末尾。
- `/error`：搜索 `error`。
- `n`：下一个搜索结果。
- `q`：退出。

查看大文件时，`less` 比 `cat` 更舒服。

### 5.3 head 和 tail：查看开头和结尾

查看前 10 行：

```bash
head app.log
```

查看前 50 行：

```bash
head -n 50 app.log
```

查看最后 10 行：

```bash
tail app.log
```

查看最后 100 行：

```bash
tail -n 100 app.log
```

实时追踪日志：

```bash
tail -f app.log
```

实时追踪并从最后 200 行开始：

```bash
tail -n 200 -f app.log
```

排查服务时很常用：

```bash
tail -f /var/log/nginx/error.log
```

### 5.4 wc：统计行数、单词数和字节数

统计文件行数：

```bash
wc -l access.log
```

统计文件大小字节数：

```bash
wc -c access.log
```

统计多个文件：

```bash
wc -l *.py
```

---

## 六、搜索文件和内容

### 6.1 find：按条件查找文件

在当前目录查找所有 `.py` 文件：

```bash
find . -name "*.py"
```

忽略大小写：

```bash
find . -iname "*.md"
```

查找目录：

```bash
find . -type d -name "logs"
```

查找普通文件：

```bash
find . -type f -name "*.log"
```

查找 7 天内修改过的文件：

```bash
find . -type f -mtime -7
```

查找 30 天前修改过的日志：

```bash
find /var/log -type f -name "*.log" -mtime +30
```

查找大于 100MB 的文件：

```bash
find . -type f -size +100M
```

找到后删除前建议先打印确认：

```bash
find . -type f -name "*.tmp"
```

确认无误后再执行：

```bash
find . -type f -name "*.tmp" -delete
```

### 6.2 grep：搜索文本内容

在文件中搜索关键词：

```bash
grep "ERROR" app.log
```

忽略大小写：

```bash
grep -i "error" app.log
```

显示行号：

```bash
grep -n "timeout" app.log
```

递归搜索目录：

```bash
grep -R "DATABASE_URL" .
```

只显示匹配文件名：

```bash
grep -Rl "TODO" .
```

排除目录：

```bash
grep -R "TODO" . --exclude-dir=.git --exclude-dir=node_modules
```

使用正则搜索：

```bash
grep -E "ERROR|WARN" app.log
```

查看匹配行前后 3 行：

```bash
grep -n -C 3 "Exception" app.log
```

只看匹配行之后 5 行：

```bash
grep -n -A 5 "Traceback" app.log
```

只看匹配行之前 5 行：

```bash
grep -n -B 5 "Traceback" app.log
```

### 6.3 rg：更快的内容搜索

`rg` 是 ripgrep，速度很快，很多开发环境都推荐使用。

搜索关键词：

```bash
rg "TODO"
```

搜索指定文件类型：

```bash
rg "requests" -g "*.py"
```

显示隐藏文件：

```bash
rg "token" --hidden
```

排除目录：

```bash
rg "password" -g "!node_modules" -g "!.git"
```

列出所有文件：

```bash
rg --files
```

在项目中找函数定义：

```bash
rg "def main"
```

---

## 七、文本处理命令

### 7.1 echo：输出文本

```bash
echo "hello"
```

查看变量：

```bash
echo $HOME
echo $PATH
```

写入文件：

```bash
echo "hello" > hello.txt
```

追加到文件：

```bash
echo "world" >> hello.txt
```

`>` 会覆盖原文件，`>>` 会追加内容。

### 7.2 sort：排序

按字典顺序排序：

```bash
sort names.txt
```

数字排序：

```bash
sort -n scores.txt
```

倒序：

```bash
sort -r names.txt
```

去重排序：

```bash
sort -u names.txt
```

按第二列数字排序：

```bash
sort -k2 -n data.txt
```

假设 `data.txt` 内容如下：

```text
alice 90
bob 75
carol 88
```

执行后会按分数升序排列。

### 7.3 uniq：去除相邻重复行

`uniq` 只处理相邻重复行，所以经常和 `sort` 搭配。

```bash
sort names.txt | uniq
```

统计重复次数：

```bash
sort names.txt | uniq -c
```

按出现次数排序：

```bash
sort names.txt | uniq -c | sort -nr
```

### 7.4 cut：按列截取

按冒号分隔，取第一列：

```bash
cut -d ":" -f 1 /etc/passwd
```

按逗号分隔，取第 1 和第 3 列：

```bash
cut -d "," -f 1,3 users.csv
```

### 7.5 awk：按列处理文本

打印第一列：

```bash
awk '{print $1}' access.log
```

打印第一列和第三列：

```bash
awk '{print $1, $3}' access.log
```

按条件过滤：

```bash
awk '$3 > 80 {print $1, $3}' scores.txt
```

统计访问日志中的 IP 次数：

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
```

### 7.6 sed：替换和编辑文本流

把文件中的 `old` 替换成 `new` 并输出到屏幕：

```bash
sed 's/old/new/g' config.txt
```

直接修改文件：

```bash
sed -i 's/old/new/g' config.txt
```

删除空行：

```bash
sed '/^$/d' notes.txt
```

打印第 10 到 20 行：

```bash
sed -n '10,20p' app.log
```

---

## 八、管道、重定向和组合命令

### 8.1 管道 |

管道把前一个命令的输出交给后一个命令处理。

查看日志中出现最多的 10 个 IP：

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -n 10
```

查找 Python 文件中包含 `TODO` 的行：

```bash
find . -name "*.py" | xargs grep -n "TODO"
```

### 8.2 重定向

覆盖写入：

```bash
ls -lh > files.txt
```

追加写入：

```bash
date >> run.log
```

把错误输出写入文件：

```bash
python app.py 2> error.log
```

把标准输出和错误输出都写入文件：

```bash
python app.py > output.log 2>&1
```

### 8.3 xargs：把输入转成参数

删除所有 `.tmp` 文件前先打印：

```bash
find . -name "*.tmp" -print
```

确认后删除：

```bash
find . -name "*.tmp" -print | xargs rm
```

如果文件名可能包含空格，用更稳妥的写法：

```bash
find . -name "*.tmp" -print0 | xargs -0 rm
```

批量统计 Python 文件行数：

```bash
find . -name "*.py" -print0 | xargs -0 wc -l
```

---

## 九、权限与用户

### 9.1 查看权限

```bash
ls -l
```

示例：

```text
-rwxr-xr-- 1 alice dev 1024 Jul  5 10:00 deploy.sh
```

权限分成三组：

- `rwx`：文件所有者权限。
- `r-x`：所属组权限。
- `r--`：其他用户权限。

含义：

- `r`：read，读。
- `w`：write，写。
- `x`：execute，执行。

### 9.2 chmod：修改权限

给脚本添加执行权限：

```bash
chmod +x deploy.sh
```

取消其他用户写权限：

```bash
chmod o-w file.txt
```

使用数字权限：

```bash
chmod 755 deploy.sh
chmod 644 config.yml
```

常见数字：

- `7 = 4 + 2 + 1`，读写执行。
- `6 = 4 + 2`，读写。
- `5 = 4 + 1`，读执行。
- `4`，只读。

所以：

- `755`：所有者可读写执行，其他人可读可执行。
- `644`：所有者可读写，其他人只读。
- `600`：只有所有者可读写，常用于私钥和敏感配置。

示例：

```bash
chmod 600 ~/.ssh/id_rsa
```

### 9.3 chown：修改所有者

把文件所有者改为 `alice`：

```bash
sudo chown alice file.txt
```

同时修改用户和用户组：

```bash
sudo chown alice:dev file.txt
```

递归修改目录：

```bash
sudo chown -R www-data:www-data /var/www/app
```

### 9.4 whoami、id、groups：查看身份

查看当前用户：

```bash
whoami
```

查看用户 ID 和组：

```bash
id
```

查看所属组：

```bash
groups
```

### 9.5 sudo：以管理员权限执行

安装软件或修改系统文件时常用：

```bash
sudo apt update
sudo systemctl restart nginx
```

不要滥用 `sudo`。如果普通用户权限能完成，就不需要提升权限。

---

## 十、进程管理

### 10.1 ps：查看进程

查看当前终端相关进程：

```bash
ps
```

查看所有进程：

```bash
ps aux
```

搜索某个进程：

```bash
ps aux | grep nginx
```

常见列含义：

- `USER`：进程所属用户。
- `PID`：进程 ID。
- `%CPU`：CPU 占用。
- `%MEM`：内存占用。
- `COMMAND`：启动命令。

### 10.2 top 和 htop：动态查看资源

```bash
top
```

常用按键：

- `P`：按 CPU 排序。
- `M`：按内存排序。
- `q`：退出。

如果安装了 `htop`，体验更好：

```bash
htop
```

### 10.3 kill：结束进程

先找到 PID：

```bash
ps aux | grep app.py
```

正常结束：

```bash
kill 12345
```

强制结束：

```bash
kill -9 12345
```

优先使用普通 `kill`，只有进程无响应时再使用 `kill -9`。

### 10.4 pkill：按名称结束进程

结束所有匹配 `python app.py` 的进程：

```bash
pkill -f "python app.py"
```

先确认匹配范围：

```bash
pgrep -af "python app.py"
```

确认后再执行 `pkill`。

### 10.5 nohup 和后台运行

后台运行命令：

```bash
python app.py &
```

退出终端后仍继续运行：

```bash
nohup python app.py > app.log 2>&1 &
```

查看后台任务：

```bash
jobs
```

把后台任务切回前台：

```bash
fg
```

---

## 十一、网络相关命令

### 11.1 ping：测试网络连通

```bash
ping baidu.com
```

指定次数：

```bash
ping -c 4 baidu.com
```

如果域名 ping 不通，可以试试 IP：

```bash
ping -c 4 8.8.8.8
```

域名不通但 IP 能通，可能是 DNS 问题。

### 11.2 curl：发送 HTTP 请求

查看网页内容：

```bash
curl https://example.com
```

只看响应头：

```bash
curl -I https://example.com
```

跟随重定向：

```bash
curl -L https://example.com
```

发送 GET 请求：

```bash
curl "https://api.example.com/users?page=1"
```

发送 POST JSON：

```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"alice","age":20}'
```

保存文件：

```bash
curl -L -o app.tar.gz https://example.com/app.tar.gz
```

### 11.3 wget：下载文件

```bash
wget https://example.com/file.zip
```

指定输出文件名：

```bash
wget -O app.zip https://example.com/file.zip
```

断点续传：

```bash
wget -c https://example.com/big-file.iso
```

### 11.4 ss：查看端口监听

查看所有监听端口：

```bash
ss -lntp
```

含义：

- `-l`：只看监听状态。
- `-n`：不解析名称，显示数字端口。
- `-t`：TCP。
- `-p`：显示进程。

查看 80 端口：

```bash
ss -lntp | grep ":80"
```

查看 8000 端口被谁占用：

```bash
ss -lntp | grep ":8000"
```

### 11.5 ip：查看网络配置

查看 IP 地址：

```bash
ip addr
```

简洁查看：

```bash
ip -brief addr
```

查看路由：

```bash
ip route
```

查看某个网卡：

```bash
ip addr show eth0
```

---

## 十二、磁盘与系统资源

### 12.1 df：查看磁盘空间

```bash
df -h
```

常见输出：

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   35G   13G  74% /
```

重点看：

- `Size`：总大小。
- `Used`：已用。
- `Avail`：可用。
- `Use%`：使用百分比。
- `Mounted on`：挂载点。

### 12.2 du：查看目录占用

查看当前目录总大小：

```bash
du -sh .
```

查看当前目录下每个子目录大小：

```bash
du -h --max-depth=1
```

按大小排序：

```bash
du -h --max-depth=1 | sort -h
```

找出当前目录下最大的 10 个文件或目录：

```bash
du -ah . | sort -rh | head -n 10
```

### 12.3 free：查看内存

```bash
free -h
```

重点看：

- `total`：总内存。
- `used`：已用内存。
- `free`：完全空闲内存。
- `available`：可供新程序使用的内存，更有参考价值。

### 12.4 uptime：查看运行时间和负载

```bash
uptime
```

示例：

```text
10:30:12 up 5 days,  2:10,  2 users,  load average: 0.12, 0.20, 0.18
```

`load average` 后面三个数字分别表示 1 分钟、5 分钟、15 分钟平均负载。

### 12.5 uname：查看系统信息

```bash
uname -a
```

查看内核版本：

```bash
uname -r
```

查看系统发行版：

```bash
cat /etc/os-release
```

---

## 十三、压缩与解压

### 13.1 tar.gz

打包并 gzip 压缩：

```bash
tar -czf project.tar.gz project/
```

解压：

```bash
tar -xzf project.tar.gz
```

解压到指定目录：

```bash
tar -xzf project.tar.gz -C /tmp
```

查看压缩包内容：

```bash
tar -tzf project.tar.gz
```

参数含义：

- `c`：create，创建包。
- `x`：extract，解包。
- `t`：list，查看内容。
- `z`：gzip。
- `f`：指定文件。

### 13.2 zip 和 unzip

压缩目录：

```bash
zip -r project.zip project/
```

解压：

```bash
unzip project.zip
```

解压到指定目录：

```bash
unzip project.zip -d /tmp/project
```

查看 zip 内容：

```bash
unzip -l project.zip
```

### 13.3 gzip 和 gunzip

压缩单个文件：

```bash
gzip app.log
```

会生成 `app.log.gz`，原文件默认会被替换。

解压：

```bash
gunzip app.log.gz
```

保留原文件压缩：

```bash
gzip -k app.log
```

---

## 十四、软件包管理

不同 Linux 发行版使用不同包管理器。

### 14.1 Debian、Ubuntu：apt

更新软件源：

```bash
sudo apt update
```

升级已安装软件：

```bash
sudo apt upgrade
```

安装软件：

```bash
sudo apt install nginx
```

卸载软件：

```bash
sudo apt remove nginx
```

搜索软件：

```bash
apt search python3
```

查看软件信息：

```bash
apt show nginx
```

### 14.2 CentOS、RHEL、Fedora：dnf 或 yum

安装软件：

```bash
sudo dnf install nginx
```

旧系统可能使用：

```bash
sudo yum install nginx
```

更新软件：

```bash
sudo dnf update
```

卸载软件：

```bash
sudo dnf remove nginx
```

搜索软件：

```bash
dnf search nginx
```

---

## 十五、服务管理 systemctl

现代 Linux 系统大多用 `systemd` 管理服务。

### 15.1 查看服务状态

```bash
systemctl status nginx
```

如果服务异常，状态里通常会显示最近的错误信息。

### 15.2 启动、停止和重启

启动服务：

```bash
sudo systemctl start nginx
```

停止服务：

```bash
sudo systemctl stop nginx
```

重启服务：

```bash
sudo systemctl restart nginx
```

重新加载配置：

```bash
sudo systemctl reload nginx
```

如果服务支持 reload，修改配置后优先使用 reload；不支持再 restart。

### 15.3 开机自启动

设置开机自启动：

```bash
sudo systemctl enable nginx
```

取消开机自启动：

```bash
sudo systemctl disable nginx
```

查看是否开机自启动：

```bash
systemctl is-enabled nginx
```

### 15.4 查看日志 journalctl

查看某个服务日志：

```bash
journalctl -u nginx
```

查看最近 100 行：

```bash
journalctl -u nginx -n 100
```

实时追踪：

```bash
journalctl -u nginx -f
```

查看今天的日志：

```bash
journalctl -u nginx --since today
```

查看某个时间段：

```bash
journalctl -u nginx --since "2026-07-05 10:00" --until "2026-07-05 11:00"
```

---

## 十六、SSH 与远程操作

### 16.1 ssh：登录远程服务器

```bash
ssh alice@192.168.1.10
```

指定端口：

```bash
ssh -p 2222 alice@192.168.1.10
```

指定私钥：

```bash
ssh -i ~/.ssh/id_rsa alice@192.168.1.10
```

第一次连接时会提示确认主机指纹，确认服务器地址无误后输入 `yes`。

### 16.2 scp：复制文件到远程服务器

本地复制到远程：

```bash
scp app.tar.gz alice@192.168.1.10:/home/alice/
```

远程复制到本地：

```bash
scp alice@192.168.1.10:/var/log/app.log .
```

复制目录：

```bash
scp -r dist/ alice@192.168.1.10:/var/www/app/
```

指定端口：

```bash
scp -P 2222 app.tar.gz alice@192.168.1.10:/home/alice/
```

注意：`ssh` 使用小写 `-p` 指定端口，`scp` 使用大写 `-P`。

### 16.3 rsync：增量同步

同步目录到远程：

```bash
rsync -av dist/ alice@192.168.1.10:/var/www/app/
```

删除远程多余文件，保持完全一致：

```bash
rsync -av --delete dist/ alice@192.168.1.10:/var/www/app/
```

先演练，不真正执行：

```bash
rsync -av --delete --dry-run dist/ alice@192.168.1.10:/var/www/app/
```

`rsync` 中路径末尾的 `/` 很重要：

```bash
rsync -av dist/ target/
```

表示把 `dist` 里面的内容同步到 `target`。

```bash
rsync -av dist target/
```

表示把整个 `dist` 目录同步到 `target/dist`。

---

## 十七、环境变量

### 17.1 查看环境变量

查看全部环境变量：

```bash
env
```

查看某个变量：

```bash
echo $HOME
echo $PATH
```

### 17.2 临时设置环境变量

只对当前终端有效：

```bash
export APP_ENV=dev
```

运行程序时临时传入：

```bash
APP_ENV=prod python app.py
```

### 17.3 写入 shell 配置

Bash 用户常见配置文件：

```bash
~/.bashrc
~/.bash_profile
```

Zsh 用户常见配置文件：

```bash
~/.zshrc
```

例如把自定义目录加入 `PATH`：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

修改后让配置立即生效：

```bash
source ~/.bashrc
```

---

## 十八、时间与定时任务

### 18.1 date：查看和格式化时间

查看当前时间：

```bash
date
```

按格式输出：

```bash
date "+%Y-%m-%d %H:%M:%S"
```

生成日志文件名：

```bash
echo "backup-$(date +%Y%m%d-%H%M%S).tar.gz"
```

### 18.2 crontab：定时任务

编辑当前用户定时任务：

```bash
crontab -e
```

查看定时任务：

```bash
crontab -l
```

定时任务格式：

```text
分 时 日 月 周 命令
```

每天凌晨 2 点执行备份：

```cron
0 2 * * * /home/alice/scripts/backup.sh
```

每 5 分钟执行一次：

```cron
*/5 * * * * /home/alice/scripts/check.sh
```

每周一 9 点执行：

```cron
0 9 * * 1 /home/alice/scripts/report.sh
```

定时任务建议写绝对路径，并把输出重定向到日志：

```cron
0 2 * * * /bin/bash /home/alice/scripts/backup.sh >> /home/alice/logs/backup.log 2>&1
```

---

## 十九、常见排错场景

### 19.1 端口被占用

问题：启动服务时报错 `Address already in use`。

查看端口：

```bash
ss -lntp | grep ":8000"
```

找到进程后查看详情：

```bash
ps -p 12345 -f
```

正常结束：

```bash
kill 12345
```

如果确认进程卡死：

```bash
kill -9 12345
```

### 19.2 磁盘满了

查看整体空间：

```bash
df -h
```

查看根目录下哪个目录大：

```bash
sudo du -h --max-depth=1 / | sort -h
```

查看当前目录最大文件：

```bash
du -ah . | sort -rh | head -n 20
```

常见可检查目录：

```bash
/var/log
/tmp
/var/cache
```

删除日志前，先确认是否还被进程占用。某些服务的日志文件删除后，空间可能不会立刻释放，需要重启服务或让服务重新打开日志文件。

### 19.3 权限不足

问题：出现 `Permission denied`。

查看文件权限：

```bash
ls -l file.txt
```

查看目录权限：

```bash
ls -ld /path/to/dir
```

查看当前用户：

```bash
whoami
id
```

如果是脚本不能执行：

```bash
chmod +x script.sh
```

如果是文件归属不对：

```bash
sudo chown alice:alice file.txt
```

### 19.4 服务启动失败

查看状态：

```bash
systemctl status nginx
```

查看日志：

```bash
journalctl -u nginx -n 100
```

实时观察：

```bash
journalctl -u nginx -f
```

如果是 Nginx 配置问题，可以先测试配置：

```bash
sudo nginx -t
```

测试通过后再重载：

```bash
sudo systemctl reload nginx
```

### 19.5 网络请求失败

先确认域名解析：

```bash
ping -c 4 example.com
```

再确认 HTTP 响应：

```bash
curl -I https://example.com
```

如果接口慢，可以查看耗时：

```bash
curl -o /dev/null -s -w "time_total=%{time_total}\n" https://example.com
```

如果需要看完整请求过程：

```bash
curl -v https://example.com
```

---

## 二十、开发中高频组合

### 20.1 查看项目里最大的文件

```bash
du -ah . | sort -rh | head -n 20
```

适合排查项目为什么变得很大。

### 20.2 统计代码行数

```bash
find . -name "*.py" -print0 | xargs -0 wc -l
```

排除虚拟环境：

```bash
find . -path "./.venv" -prune -o -name "*.py" -print0 | xargs -0 wc -l
```

### 20.3 搜索配置里的敏感词

```bash
rg -i "password|secret|token|api_key" .
```

提交代码前可以检查是否误提交密钥。

### 20.4 查看最近修改的文件

```bash
find . -type f -mtime -1
```

查看最近 1 小时修改过的文件：

```bash
find . -type f -mmin -60
```

### 20.5 快速备份目录

```bash
tar -czf "project-$(date +%Y%m%d-%H%M%S).tar.gz" project/
```

生成类似：

```text
project-20260705-103012.tar.gz
```

### 20.6 查看日志中错误最多的接口

假设访问日志第 7 列是 URL，第 9 列是状态码：

```bash
awk '$9 >= 500 {print $7}' access.log | sort | uniq -c | sort -nr | head
```

这个组合可以帮助快速定位后端报错集中的接口。

### 20.7 查看某个进程打开了哪些文件

如果系统安装了 `lsof`：

```bash
lsof -p 12345
```

查看某个端口：

```bash
lsof -i :8000
```

查看某个文件被谁占用：

```bash
lsof /var/log/app.log
```

---

## 二十一、学习建议

不要一开始就试图背完所有命令。更好的方式是按场景记忆：

- 想知道自己在哪：`pwd`
- 想去某个目录：`cd`
- 想看目录里有什么：`ls -lh`
- 想看文件内容：`less`、`head`、`tail`
- 想找文件：`find`
- 想搜内容：`grep` 或 `rg`
- 想看磁盘：`df -h`、`du -sh`
- 想看进程：`ps aux`、`top`
- 想看端口：`ss -lntp`
- 想看服务：`systemctl status`
- 想看日志：`tail -f`、`journalctl -f`

真正熟练的关键不是一次记住很多命令，而是每次遇到问题都能形成固定排查路径。比如服务访问不了，可以按这个顺序：

```bash
systemctl status 服务名
journalctl -u 服务名 -n 100
ss -lntp | grep 端口
curl -I http://127.0.0.1:端口
df -h
free -h
```

这套流程能覆盖很多日常问题。用得多了，命令自然会变成肌肉记忆。
