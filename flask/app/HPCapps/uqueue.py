import subprocess

CMD_PATH = "/var/www/hpc-gbjh.app.intra/html/HPCapps"


def getGrid():
    get_queueinfo = subprocess.Popen(
        [f"{CMD_PATH}/get-queueinfo.sh"],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        close_fds=True,
        encoding="UTF-8",
        universal_newlines=True,
    )

    return get_queueinfo.communicate()[0]


def getGridXML():
    get_queueinfo = subprocess.Popen(
        [f"{CMD_PATH}/get-queueinfoxml.sh"],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        close_fds=True,
        encoding="UTF-8",
        universal_newlines=True,
    )

    return get_queueinfo.communicate()[0]


def getGridHistory():
    get_queueinfo = subprocess.Popen(
        [f"{CMD_PATH}/get-queuehistory.sh"],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        close_fds=True,
        encoding="UTF-8",
        universal_newlines=True,
    )

    return get_queueinfo.communicate()[0]
