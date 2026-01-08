"""
案例检索工具 - 在 cases 目录下搜索相关案例
"""

import os
import re
from typing import List, Tuple


def search_cases(query: str, cases_dir: str = "cases") -> str:
    """
    在 cases 目录下所有 .md 文件中搜索
    支持 OR 匹配（任意关键词出现），按匹配数排序，返回最匹配的 top 3 片段
    每个片段包含前10行+匹配行+后10行（共21行），每个文件最多处理5个匹配位置
    
    Args:
        query: 搜索关键词（空格分隔）
        cases_dir: 案例目录路径
    
    Returns:
        检索结果字符串
    """
    if not os.path.exists(cases_dir):
        return "错误：案例目录不存在"

    # 优化关键词提取：去除标点，保留中文和英文
    query_clean = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', query)
    keywords = [kw.strip() for kw in re.split(r'\s+', query_clean.lower()) if kw.strip()]
    
    # 如果关键词为空，返回失败
    if not keywords:
        return "未找到相关案例，请尝试简化关键词"
    all_snippets: List[Tuple[str, int, str]] = []  # (文件名, 匹配度, snippet)

    # 遍历所有文件，收集所有匹配位置的片段
    for filename in os.listdir(cases_dir):
        # 排除 README 文件
        if filename.lower() == "readme.md":
            continue
        if filename.endswith(".md"):
            filepath = os.path.join(cases_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content_lower = content.lower()
                    lines = content.split('\n')

                    # 找到所有匹配的行位置（支持部分匹配）
                    match_positions = []
                    for i, line in enumerate(lines):
                        line_lower = line.lower()
                        matches_in_line = 0
                        # 优先匹配完整关键词
                        for kw in keywords:
                            if kw in line_lower:
                                matches_in_line += 2  # 完整匹配权重更高
                            elif len(kw) >= 2:
                                # 如果关键词长度>=2，尝试部分匹配（关键词的一部分）
                                for j in range(len(kw) - 1):
                                    if kw[j:j+2] in line_lower:
                                        matches_in_line += 1  # 部分匹配权重较低
                                        break
                        
                        if matches_in_line > 0:
                            match_positions.append((i, matches_in_line))
                    
                    # 按匹配度排序，优先处理匹配度高的行
                    match_positions.sort(key=lambda x: x[1], reverse=True)
                    match_positions = [pos[0] for pos in match_positions[:5]]  # 每个文件最多处理5个匹配位置

                    # 对每个匹配位置提取上下文（前10行非空行 + 匹配行 + 后10行非空行，共21行）
                    for match_line in match_positions:
                        # 向前找10个非空行
                        non_empty_before = []
                        i = match_line - 1
                        while i >= 0 and len(non_empty_before) < 10:
                            if lines[i].strip():  # 非空行
                                non_empty_before.insert(0, i)
                            i -= 1
                        
                        # 向后找10个非空行
                        non_empty_after = []
                        i = match_line + 1
                        while i < len(lines) and len(non_empty_after) < 10:
                            if lines[i].strip():  # 非空行
                                non_empty_after.append(i)
                            i += 1
                        
                        # 组合片段：前7行非空 + 匹配行 + 后7行非空
                        snippet_indices = non_empty_before + [match_line] + non_empty_after
                        snippet_lines = [lines[idx] for idx in snippet_indices]
                        snippet = '\n'.join(snippet_lines)
                        
                        # 计算该片段的匹配度（片段中关键词出现次数）
                        snippet_lower = snippet.lower()
                        snippet_score = sum(snippet_lower.count(kw) for kw in keywords)
                        
                        all_snippets.append((filename, snippet_score, snippet))
            except Exception:
                continue

    if not all_snippets:
        return "未找到相关案例，请尝试简化关键词"

    # 按匹配度降序排序，取 top 3 最匹配的片段
    all_snippets.sort(key=lambda x: x[1], reverse=True)
    results = []
    for filename, score, snippet in all_snippets[:3]:
        results.append(f"【来源：{filename} | 匹配度：{score}】\n{snippet}\n")

    return "\n---\n".join(results)

