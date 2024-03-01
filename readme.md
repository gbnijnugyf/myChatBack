项目路径：'/root/autodl-tmp/myChat/myChat/'

后台运行：nohup /root/miniconda3/envs/chat_llava/bin/python /root/autodl-tmp/myChat/myChat/src/application.py >> /root/autodl-tmp/myChat/output.txt &
查找进程：ps aux | grep "/root/autodl-tmp/myChat/myChat/src/application.py" 这个命令会返回一些信息，其中第二列就是PID。
杀死进程：kill -9 PID

数据库恢复： mysql -u root -p my_chat < /root/autodl-tmp/myChat/my_chat_backup.sql