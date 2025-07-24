# -*- coding: utf-8 -*-
# @Author  : LG

import codecs
from setuptools import setup, find_packages

def get_version():
    try:
        from ISAT_plugin_mask_export.__init__ import __version__
        return __version__

    except FileExistsError:
        FileExistsError('__init__.py not exists.')

setup(
    name="isat-plugin-mask-export",                                        # 包名
    version=get_version(),                                                 # 版本号
    author="yatengLG",
    author_email="yatenglg@foxmail.com",
    description="ISAT Plugin for mask export.",
    long_description=(codecs.open("README.md", encoding='utf-8').read()),
    long_description_content_type="text/markdown",

    url="https://github.com/yatengLG/ISAT_plugin_mask_export",  # 项目相关文件地址

    keywords=["isat-sam", "isat plugin", "mask export"],
    license="Apache2.0",

    packages=find_packages(),
    include_package_data=True,

    python_requires=">=3.8",                            # python 版本要求
    install_requires=[
        'isat-sam>=1.4.0',
    ],

    classifiers=[
        "Intended Audience :: Developers",              # 目标用户:开发者
        "Intended Audience :: Science/Research",        # 目标用户:学者
        'Development Status :: 5 - Production/Stable',
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
        'License :: OSI Approved :: Apache Software License',

        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],

    entry_points={
        "isat.plugins": [
            "mask_export_plugin = ISAT_plugin_mask_export.main:MaskExportPlugin",
        ]
    }
)
