# 检测字符串是不是全是英文字母
def IsStrAllAlpha(str: str) -> bool:
    return str.encode().isalpha()


# 尝试把str转为int，如果失败了返回字符串自身
def TryStr2Int(str: str):
    try:
        res = int(str)
        return True, res
    except:
        return False, str
