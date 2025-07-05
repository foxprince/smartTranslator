#!/usr/bin/env python3
"""
测试运行脚本
提供多种测试运行选项和报告生成
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并处理结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description or cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"\n✅ 成功: {description or cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 失败: {description or cmd}")
        print(f"错误代码: {e.returncode}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="翻译系统测试运行器")
    
    # 测试类型选项
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "api", "all"],
        default="all",
        help="测试类型 (默认: all)"
    )
    
    # 覆盖率选项
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="生成覆盖率报告"
    )
    
    # 详细输出
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    # 快速模式（跳过慢速测试）
    parser.add_argument(
        "--fast",
        action="store_true",
        help="快速模式，跳过慢速测试"
    )
    
    # 并行测试
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="并行测试进程数 (默认: 1)"
    )
    
    # 特定测试文件
    parser.add_argument(
        "--file",
        help="运行特定测试文件"
    )
    
    # 特定测试函数
    parser.add_argument(
        "--test",
        help="运行特定测试函数"
    )
    
    # 生成报告
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成HTML测试报告"
    )
    
    args = parser.parse_args()
    
    # 确保在正确的目录
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # 检查依赖
    print("🔍 检查测试依赖...")
    required_packages = ["pytest", "pytest-asyncio", "pytest-cov", "httpx"]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            print(f"❌ 缺少依赖: {package}")
            print(f"请运行: pip install {package}")
            sys.exit(1)
    
    print("✅ 所有依赖已安装")
    
    # 构建pytest命令
    cmd_parts = ["python", "-m", "pytest"]
    
    # 添加基本选项
    if args.verbose:
        cmd_parts.append("-v")
    else:
        cmd_parts.append("-q")
    
    # 添加并行选项
    if args.parallel > 1:
        cmd_parts.extend(["-n", str(args.parallel)])
    
    # 添加覆盖率选项
    if args.coverage:
        cmd_parts.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=70"
        ])
    
    # 添加测试类型过滤
    if args.type != "all":
        cmd_parts.extend(["-m", args.type])
    
    # 跳过慢速测试
    if args.fast:
        if args.type == "all":
            cmd_parts.extend(["-m", "not slow"])
        else:
            cmd_parts.extend(["-m", f"{args.type} and not slow"])
    
    # 特定文件或测试
    if args.file:
        cmd_parts.append(f"tests/{args.file}")
    elif args.test:
        cmd_parts.extend(["-k", args.test])
    else:
        cmd_parts.append("tests/")
    
    # 添加报告选项
    if args.report:
        cmd_parts.extend([
            "--html=reports/test_report.html",
            "--self-contained-html"
        ])
        # 确保报告目录存在
        os.makedirs("reports", exist_ok=True)
    
    # 运行测试
    cmd = " ".join(cmd_parts)
    success = run_command(cmd, "运行测试套件")
    
    if success:
        print(f"\n🎉 测试完成!")
        
        # 显示覆盖率报告位置
        if args.coverage:
            coverage_html = backend_dir / "htmlcov" / "index.html"
            if coverage_html.exists():
                print(f"📊 覆盖率报告: file://{coverage_html.absolute()}")
        
        # 显示测试报告位置
        if args.report:
            test_report = backend_dir / "reports" / "test_report.html"
            if test_report.exists():
                print(f"📋 测试报告: file://{test_report.absolute()}")
        
        # 运行代码质量检查
        print(f"\n🔍 运行代码质量检查...")
        
        # Flake8检查
        if run_command("flake8 app/ --max-line-length=100 --ignore=E203,W503", "代码风格检查"):
            print("✅ 代码风格检查通过")
        
        # MyPy类型检查
        if run_command("mypy app/ --ignore-missing-imports", "类型检查"):
            print("✅ 类型检查通过")
        
        print(f"\n{'='*60}")
        print("🎯 测试总结:")
        print(f"  测试类型: {args.type}")
        print(f"  覆盖率报告: {'是' if args.coverage else '否'}")
        print(f"  HTML报告: {'是' if args.report else '否'}")
        print(f"  并行进程: {args.parallel}")
        print(f"{'='*60}")
        
    else:
        print(f"\n💥 测试失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
