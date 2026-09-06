#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate admin/config.yml for Decap CMS from content/*.json structure.
Field structure mirrors the JSON exactly so Decap never drops keys on save."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "admin" / "config.yml"

# Chinese labels; key name fallback is the raw key.
LABELS = {
    # generic
    "title": "标题 / Title", "name": "名称 / Name", "desc": "描述 / Description",
    "text": "文本 / Text", "lead": "导语 / Lead", "note": "备注 / Note",
    "tags": "标签 / Tags", "link": "链接文字 / Link text",
    "eyebrow": "栏目眉标 / Eyebrow",
    # settings
    "site": "站点", "meta": "SEO 元信息", "nav": "导航", "footer": "页脚",
    "brand_name": "品牌名 / Brand", "nav_home": "导航-首页", "nav_about": "导航-关于我们",
    "nav_products": "导航-产品", "nav_oem": "导航-OEM/ODM", "nav_contact": "导航-联系",
    "cta_quote": "CTA 按钮文字（询价）", "sample_tag": "示例标签文字",
    "sample_notice": "示例声明（加粗部分）", "footer_desc": "页脚简介",
    "footer_site_title": "页脚-站点标题", "footer_contact_title": "页脚-联系标题",
    "footer_copyright": "版权年份", "footer_company": "版权公司名",
    "footer_privacy": "页脚-隐私链接", "footer_terms": "页脚-条款链接",
    "footer_accessibility": "页脚-无障碍链接",
    # hero
    "hero": "首屏 Hero", "title1": "主标题（第一行）", "title2": "主标题（第二行, 高亮）",
    "cta_secondary": "次按钮文字", "sample_note": "示例注记",
    "proof_title": "覆盖区域标题", "proof0": "覆盖区域 1", "proof1": "覆盖区域 2",
    "proof2": "覆盖区域 3", "title_key": "", "text_key": "副文字",
    # product lines
    "product-lines": "产品线", "items": "剂型卡片（最多5项）", "item": "剂型",
    # services
    "services": "合作方式", "cards": "合作卡片", "card": "方式",
    # capabilities
    "capabilities": "能力与资质", "features": "能力项", "feature": "能力",
    "credentials": "资质声明", "text_html": "资质正文（可含强调标签）",
    # markets
    "markets": "目标市场", "regions": "区域列表", "region": "区域",
    "note_compliance": "合规备注（每区域）", "note_logistics": "物流备注（每区域）",
    # about
    "about": "关于我们", "story_header": "公司故事正文", "cells": "四大板块（R&D/产能/质控/供应链）",
    "cell": "板块",
    # products
    "products": "产品分类", "categories": "分类列表", "category": "分类",
    "boundary": "边界声明", "p1_before": "边界声明第一段（含示例加粗）",
    "p2": "边界声明第二段",
    # oem
    "oem": "OEM/ODM 服务", "steps": "流程步骤（8步）", "step": "步骤",
    # contact
    "contact": "联系表单", "form": "表单设置", "direct": "直接联系方式",
    "name_label": "姓名标签", "email_label": "邮箱标签", "company_label": "公司标签",
    "market_label": "目标市场标签", "market_placeholder": "市场占位选项",
    "market_europe": "选项：欧洲", "market_us": "选项：美国",
    "market_seasia": "选项：东南亚", "market_global": "选项：全球/其他",
    "message_label": "留言标签", "message_placeholder": "留言占位提示",
    "submit": "提交按钮", "privacy_note": "隐私声明",
    "email": "邮箱", "location": "地址", "response": "响应时间",
    "whatsapp": "WhatsApp", "website": "官网", "website_url": "官网链接",
    "website_text": "官网显示文字", "email_prefix": "邮箱（链接）", "email_text": "邮箱（显示）",
    "location_label": "地址标签", "response_label": "响应时间标签",
    "whatsapp_label": "WhatsApp 标签", "website_label": "官网标签",
    "email_label2": "邮箱标签",
}


def yaml_str(s):
    """Quote a string as YAML single-quoted (escape ' as '')."""
    return "'" + str(s).replace("'", "''") + "'"


def gen_fields(node, key_hint=""):
    """Return (yaml_fields_string, is_simple)."""
    if isinstance(node, dict):
        lines = ["fields:"]
        for k, v in node.items():
            label = LABELS.get(k, k)
            if isinstance(v, dict):
                sub, _ = gen_fields(v, k)
                lines.append(f"  - name: {yaml_str(k)}")
                lines.append(f"    label: {yaml_str(label)}")
                lines.append(f"    widget: object")
                for l in sub.splitlines():
                    lines.append("    " + l if l else "")
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                sub, _ = gen_fields(v[0], k)
                lines.append(f"  - name: {yaml_str(k)}")
                lines.append(f"    label: {yaml_str(label)}")
                lines.append(f"    widget: list")
                item_label = LABELS.get(k.rstrip('s'), k.rstrip('s'))
                lines.append(f"    summary: '{item_label}: {{fields.{list(v[0].keys())[0]}}}'")
                for l in sub.splitlines():
                    lines.append("    " + l if l else "")
            else:
                lines.append(f"  - name: {yaml_str(k)}")
                lines.append(f"    label: {yaml_str(label)}")
                lines.append(f"    widget: text")
        return "\n".join(lines), False
    return "", True


COLLECTIONS = [
    # (file, name, label, description)
    ("settings.json", "settings", "站点设置", "品牌、导航、页脚与全站通用文案"),
    ("home.json", "home", "首屏 Hero", "首屏主视觉文案与区域覆盖说明"),
    ("product-lines.json", "product-lines", "产品线", "五大剂型卡片"),
    ("services.json", "services", "合作方式", "批发 / OEM / ODM 三种合作"),
    ("capabilities.json", "capabilities", "能力与资质", "四大能力与资质声明"),
    ("markets.json", "markets", "目标市场", "欧洲 / 美国 / 东南亚"),
    ("about.json", "about", "关于我们", "公司故事与四大板块"),
    ("products.json", "products", "产品分类", "四大品类与边界声明"),
    ("oem.json", "oem", "OEM 流程", "八步流程与能力边界"),
    ("contact.json", "contact", "联系表单", "表单文案与直接联系方式"),
]


def main():
    config = []
    config.append("# Decap CMS 配置文件 — Zili Nutrition 外贸独立站")
    config.append("# 认证链路：Netlify 标准路径。正式启用前需：")
    config.append("#   1. 注册免费 Netlify 账号（app.netlify.com）")
    config.append("#   2. 任意新建一个 Site（或直接对接本仓库），启用 GitHub OAuth")
    config.append("#   3. 保存 Site 后，把以下两项填入 backend：")
    config.append("#        base_url: https://api.netlify.com")
    config.append("#        auth_endpoint: auth")
    config.append("#     并在 admin/index.html 保留 netlify-identity-widget.js 引用")
    config.append("")
    config.append("backend:")
    config.append("  name: github")
    config.append("  repo: zilinutrition-arch/zili-nutrition-site")
    config.append("  branch: main")
    config.append("# Netlify 隐式 OAuth（注册后取消注释填入）")
    config.append("#  base_url: https://api.netlify.com")
    config.append("#  auth_endpoint: auth")
    config.append("")
    config.append("local_backend: false")
    config.append("")
    config.append("# 后台图片上传会提交到仓库 media/ 目录")
    config.append("media_folder: 'media'")
    config.append("public_folder: '/media'")
    config.append("")
    config.append("site_url: https://zvitahealth.com")
    config.append("")
    config.append("collections:")

    for file_name, name, label, desc in COLLECTIONS:
        payload = json.loads((CONTENT / file_name).read_text(encoding="utf-8"))
        fields, _ = gen_fields(payload)
        config.append(f"  - name: {yaml_str(name)}")
        config.append(f"    label: {yaml_str(label)}")
        config.append(f"    description: {yaml_str(desc)}")
        config.append(f"    editor: {{ preview: false }}")
        config.append("    format: json")
        config.append(f"    files:")
        config.append(f"      - name: {yaml_str(name)}")
        config.append(f"        label: {yaml_str(label)}")
        config.append(f"        file: {yaml_str('content/' + file_name)}")
        config.append(f"        fields:")
        for line in fields.splitlines()[1:]:  # skip leading "fields:"
            config.append("          " + line)

    OUT.write_text("\n".join(config) + "\n", encoding="utf-8")
    print(f"written: {OUT} ({len(config)} lines)")


if __name__ == "__main__":
    main()