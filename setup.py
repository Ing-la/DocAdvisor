"""
DocAdvisor 项目安装配置（Web 版）
"""

from setuptools import setup, find_packages
import os


def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []


setup(
    name="docadvisor",
    version="2.0.0",
    description="基于 ReAct + RAG 的 Web 文档智能顾问系统",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="DocAdvisor Team",
    packages=find_packages(exclude=['tests', 'docs', 'frontend']),
    install_requires=read_requirements(),
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'docadvisor-api=scripts.api_server:main',
        ],
    },
    include_package_data=True,
)
