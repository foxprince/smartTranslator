#!/usr/bin/env python3
"""
手动API测试脚本
"""
import requests
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """测试健康检查"""
    print("=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_document_health():
    """测试文档服务健康检查"""
    print("=== 测试文档服务健康检查 ===")
    response = requests.get(f"{BASE_URL}/api/v1/documents/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_preprocess_simple():
    """测试简单文档预处理"""
    print("=== 测试简单文档预处理 ===")
    
    test_content = """第一章 测试文档

这是第一段内容。

短

这是第二段比较长的内容，用来测试文本预处理功能。

结束。
"""
    
    data = {
        "file_content": test_content,
        "filename": "test.txt"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/documents/preprocess", json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"处理成功: {result['success']}")
        print(f"消息: {result['message']}")
        
        # 显示处理报告
        report = result['data']['processing_report']
        print(f"\n原始统计:")
        print(f"  总行数: {report['original_stats']['total_lines']}")
        print(f"  空行数: {report['original_stats']['empty_lines']}")
        print(f"  内容行数: {report['original_stats']['content_lines']}")
        print(f"  短行数: {report['original_stats']['short_lines']}")
        
        print(f"\n清理后统计:")
        print(f"  总行数: {report['cleaned_stats']['total_lines']}")
        print(f"  空行数: {report['cleaned_stats']['empty_lines']}")
        print(f"  内容行数: {report['cleaned_stats']['content_lines']}")
        print(f"  短行数: {report['cleaned_stats']['short_lines']}")
        
        print(f"\n处理时间: {report['processing_time']}秒")
        print(f"发现问题数: {len(report['issues_found'])}")
        print(f"执行的修改: {report['changes_made']}")
        
        print(f"\n清理后内容:")
        print(result['data']['cleaned_content'])
    else:
        print(f"错误: {response.text}")
    print()

if __name__ == "__main__":
    try:
        test_health_check()
        test_document_health()
        test_preprocess_simple()
        print("✅ 所有测试完成!")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
