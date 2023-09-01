import xml.etree.ElementTree as ET
import pymysql
import re
import datetime
import subprocess
import os

# 定义一个函数来执行数据库查询


class CodeScan:
    def __init__(self, logger, db: pymysql.Connection, config):
        """
        初始化 CodeScan 类。

        Args:
            logger (Logger): 用于记录消息的日志实例。
            db (pymysql.Connection): 数据库连接实例。
            config (dict): 代码扫描的配置设置。
        """
        self.logger = logger
        self.db = db
        self.config = config

    def dbquery(self, query, arg=()):
        self.db.ping(reconnect=True)
        cu = self.db.cursor()
        cu.execute(query, arg)
        ret = cu.fetchall()
        self.db.commit()
        cu.close()
        return ret

    def startScan(self):
        """
        开始代码扫描过程。
        """
        code_directory = self.config['code_path']

        # 在开始扫描之前执行 'git pull'
        git_pull_command = ["git", "pull"]
        try:
            subprocess.run(git_pull_command, check=True, cwd=code_directory)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"运行 'git pull' 时出错：{e}")
            return
        
        # 运行 'tscancode' 进行代码扫描
        scan_command = ["./Tscancode/tscancode", "-q", "--xml", "-j8", code_directory]
        try:
            scan_result = subprocess.run(scan_command, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"运行 tscancode 时出错：{e}")
            return
        
        scan_stderr = scan_result.stderr.decode('utf-8', errors='replace')

        # 处理扫描结果
        self.processScanResults(scan_stderr)

    def processScanResults(self, scan_output):
        """
        处理扫描结果。

        Args:
            scan_output (str): 以 XML 格式的扫描结果。
        """
        # 从标准错误流解析扫描结果
        root = ET.fromstring(scan_output)

        self.logger.info("Saving results to database...")

        # 处理每个错误条目并上传到数据库
        for entry in root:
            entry.set("content", re.sub(r"(\d+:)", r"\n\1", entry.get("content"))[1:])
            if not self.checkExist(entry):
                self.insertOne(entry)
        self.logger.info("Results saved")

    def insertOne(self, error_entry: ET.Element):
        """
        向数据库插入单个错误条目。

        Args:
            error_entry (ET.Element): 要插入的错误条目。
        """
        date = str(datetime.datetime.now().date())
        orgfile = error_entry.get("file")
        propath = self.config['code_path']
        filename = os.path.relpath(orgfile, propath)
        sql = "INSERT INTO `result_list` (`level`, `file`, `line`, `errortype`, `errorinfo`, `msg`, `content`, `date`, `last_show`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.dbquery(sql, (error_entry.get("severity"), filename, error_entry.get("line"), error_entry.get("id"), error_entry.get("subid"), error_entry.get("msg"), error_entry.get("content"), date, date))

    def updateRecord(self, id):
        """
        更新数据库中的记录。

        Args:
            id: 要更新的记录的 ID。
        """

        date = str(datetime.datetime.now().date())
        sql = "UPDATE result_list SET `last_show`= %s WHERE id = %s"
        self.dbquery(sql, (date, id))

    def checkExist(self, error_entry: ET.Element):
        """
        检查数据库中是否已存在相同的错误条目。

        Args:
            error_entry (ET.Element): 要检查的错误条目。

        Returns:
            bool: 如果错误条目已存在则返回 True，否则返回 False。
        """
        orgfile = error_entry.get("file")
        propath = self.config['code_path']
        filename = os.path.relpath(orgfile, propath)
        sql = "SELECT id FROM result_list WHERE file = %s AND line = %s AND errortype = %s AND errorinfo = %s"
        ret = self.dbquery(sql, (filename, error_entry.get("line"), error_entry.get("id"), error_entry.get("subid")))
        if ret.__len__() == 0:
            return False
        else:
            self.updateRecord(ret[0][0])
            return True

    def xml2db(self):
        f = open("Tscancode/output.xml", 'rb')
        content_bytes = f.read()
        decoded_string = content_bytes.decode('utf-8', errors='replace')
        root = ET.fromstring(decoded_string)
        for entry in root:
            entry.set("content", re.sub(r'(\d+:)', r'\n\1', entry.get('content'))[1:])
            if not self.checkExist(entry):
                self.insertOne(entry)
        f.close()


# config = json.load(open('config.json',encoding='utf8'))
# db = pymysql.connect(host=config['mysql_host'],user=config['mysql_user'],passwd=config['mysql_password'],database=config['mysql_database'])
# aa=CodeScan(logging.getLogger(),db,config)
# aa.startScan()