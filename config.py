import multiprocessing
bind = '0.0.0.0:8181'        # 绑定ip和端口号
# backlog = 512              # 未决连接的最大数量，即等待服务的客户的数量。默认2048个，一般不修改；
# chdir = ''                 # gunicorn要切换到的工作目录
timeout = 600                 # 超时后任务将被杀掉，并重新启动。一般设定为30秒
worker_class = 'sync'        # 使用gevent模式，还可以使用sync 模式，默认的是sync模式
workers = multiprocessing.cpu_count() * 2 + 1    # 进程数
threads = 4      # 指定每个进程开启的线程数
daemon = False   # 是否以守护进程启动，默认false
# pidfile = '/home/wwww/python/gunicorn.pid'          # 设置进程文件目录
# accesslog = '/home/wwww/python/gunicorn_acess.log'  # 设置访问日志路径
# errorlog = '/home/wwww/python/gunicorn_error.log'   # 设置错误信息日志路径
# loglevel = 'warning'                                # 设置日志记录等级

# gunicorn配置文件详解: https://blog.csdn.net/sinat_42483341/article/details/103007231