# Office 文件解析核心：xlsx/docx 标准库实现（zipfile + xml），无第三方依赖
# 说明：xlsx/docx 本质是 zip+XML，此处手工解析表格内容，避免引入 openpyxl/python-docx 依赖
# @author 6588 万立鹏 @date 2026-09-01
import io
import re
import zipfile
import xml.etree.ElementTree as ET

# OOXML 命名空间
NS_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NS_XL = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _w_text(node) -> str:
    """
    提取 Word XML 节点下所有 w:t 文本并拼接
    """
    return "".join(t.text or "" for t in node.iter(f"{NS_W}t"))


def parse_docx_bytes(data: bytes) -> str:
    """
    解析 Word(.docx)：提取段落文本与表格内容，表格行输出为 TSV
    :param data: docx 文件字节
    :return: 表格文本（TSV 行）
    """
    lines = []
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    body = root.find(f"{NS_W}body")
    for child in body:
        # 表格：每行单元格用制表符拼接
        if child.tag == f"{NS_W}tbl":
            for tr in child.iter(f"{NS_W}tr"):
                cells = [_w_text(tc).strip() for tc in tr.findall(f"{NS_W}tc")]
                lines.append("\t".join(cells))
            lines.append("")
        # 段落：非空文本直接输出
        elif child.tag == f"{NS_W}p":
            text = _w_text(child).strip()
            if text:
                lines.append(text)
    return "\n".join(lines)


def _col_index(ref: str) -> int:
    """
    Excel 单元格引用（如 B3）转列号（B -> 1），仅取字母部分
    """
    match = re.match(r"[A-Z]+", ref or "A")
    index = 0
    for ch in (match.group() if match else "A"):
        index = index * 26 + (ord(ch) - ord("A") + 1)
    return index - 1


def parse_xlsx_bytes(data: bytes) -> str:
    """
    解析 Excel(.xlsx)：所有 sheet 的行输出为 TSV（支持共享字符串与内联字符串）
    :param data: xlsx 文件字节
    :return: 表格文本（TSV 行）
    """
    lines = []
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        # 1. 共享字符串表（单元格 type=s 时按索引引用）
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            sst = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in sst.findall(f"{NS_XL}si"):
                shared.append("".join(t.text or "" for t in si.iter(f"{NS_XL}t")))
        # 2. 遍历全部 sheet
        sheet_names = [n for n in zf.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)]
        for sheet_name in sorted(sheet_names):
            root = ET.fromstring(zf.read(sheet_name))
            for row in root.iter(f"{NS_XL}row"):
                # 按列号补齐空单元格，保持列对齐
                cells_by_col = {}
                for c in row.findall(f"{NS_XL}c"):
                    ctype = c.get("t", "n")
                    v_node = c.find(f"{NS_XL}v")
                    is_node = c.find(f"{NS_XL}is")
                    if ctype == "s" and v_node is not None:
                        # 共享字符串
                        text = shared[int(v_node.text)] if v_node.text and v_node.text.isdigit() and int(v_node.text) < len(shared) else ""
                    elif ctype == "inlineStr" and is_node is not None:
                        # 内联字符串
                        text = "".join(t.text or "" for t in is_node.iter(f"{NS_XL}t"))
                    else:
                        # 数字/其他
                        text = (v_node.text or "") if v_node is not None else ""
                    cells_by_col[_col_index(c.get("r"))] = (text or "").strip()
                if cells_by_col:
                    max_col = max(cells_by_col)
                    cells = [cells_by_col.get(i, "") for i in range(max_col + 1)]
                    if any(cells):
                        lines.append("\t".join(cells))
    return "\n".join(lines)
