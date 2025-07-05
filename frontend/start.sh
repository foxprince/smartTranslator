#!/bin/bash

# 翻译系统前端启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
翻译系统前端启动脚本

用法: $0 [选项] [命令]

命令:
    dev         开发模式启动
    build       构建生产版本
    test        运行测试
    lint        代码检查
    format      代码格式化
    install     安装依赖
    clean       清理构建文件

选项:
    -h, --help      显示帮助信息
    -p, --port      指定端口 (默认: 3000)
    --host          指定主机 (默认: localhost)
    --open          自动打开浏览器

示例:
    $0 dev                    # 开发模式启动
    $0 build                  # 构建生产版本
    $0 dev -p 3001           # 指定端口启动
    $0 install               # 安装依赖

EOF
}

# 默认配置
PORT=3000
HOST="localhost"
OPEN_BROWSER=false
COMMAND=""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --open)
            OPEN_BROWSER=true
            shift
            ;;
        dev|build|test|lint|format|install|clean)
            COMMAND="$1"
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 如果没有指定命令，默认为dev
if [[ -z "$COMMAND" ]]; then
    COMMAND="dev"
fi

# 检查Node.js环境
check_node() {
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
    
    node_version=$(node -v | sed 's/v//')
    required_version="16.0.0"
    
    if [[ "$(printf '%s\n' "$required_version" "$node_version" | sort -V | head -n1)" != "$required_version" ]]; then
        log_error "需要Node.js 16.0.0或更高版本，当前版本: $node_version"
        exit 1
    fi
    
    log_info "Node.js版本: $node_version"
}

# 检查npm/yarn
check_package_manager() {
    if command -v yarn &> /dev/null; then
        PACKAGE_MANAGER="yarn"
        log_info "使用 Yarn 作为包管理器"
    elif command -v npm &> /dev/null; then
        PACKAGE_MANAGER="npm"
        log_info "使用 npm 作为包管理器"
    else
        log_error "未找到包管理器 (npm 或 yarn)"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖..."
    
    if [[ ! -f "package.json" ]]; then
        log_error "package.json 文件不存在"
        exit 1
    fi
    
    if [[ "$PACKAGE_MANAGER" == "yarn" ]]; then
        yarn install
    else
        npm install --legacy-peer-deps
    fi
    
    log_info "依赖安装完成"
}

# 检查依赖
check_dependencies() {
    if [[ ! -d "node_modules" ]]; then
        log_warn "node_modules 目录不存在，正在安装依赖..."
        install_dependencies
    fi
}

# 设置环境变量
setup_environment() {
    export PORT="$PORT"
    export HOST="$HOST"
    export BROWSER=$(if [[ "$OPEN_BROWSER" == "true" ]]; then echo "default"; else echo "none"; fi)
    export GENERATE_SOURCEMAP=true
    export REACT_APP_API_BASE_URL="http://localhost:8000"
    
    log_info "环境变量已设置"
    log_info "  PORT: $PORT"
    log_info "  HOST: $HOST"
    log_info "  API_BASE_URL: $REACT_APP_API_BASE_URL"
}

# 开发模式启动
start_dev() {
    log_info "启动开发模式..."
    
    setup_environment
    
    if [[ "$PACKAGE_MANAGER" == "yarn" ]]; then
        yarn start
    else
        npm start
    fi
}

# 构建生产版本
build_prod() {
    log_info "构建生产版本..."
    
    export NODE_ENV=production
    export GENERATE_SOURCEMAP=false
    
    if [[ "$PACKAGE_MANAGER" == "yarn" ]]; then
        yarn build
    else
        npm run build
    fi
    
    log_info "构建完成，输出目录: build/"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    if [[ "$PACKAGE_MANAGER" == "yarn" ]]; then
        yarn test --watchAll=false
    else
        npm test -- --watchAll=false
    fi
}

# 代码检查
run_lint() {
    log_info "运行代码检查..."
    
    if [[ "$PACKAGE_MANAGER" == "yarn" ]]; then
        yarn lint
    else
        npm run lint
    fi
}

# 代码格式化
run_format() {
    log_info "运行代码格式化..."
    
    if [[ "$PACKAGE_MANAGER" == "yarn" ]]; then
        yarn format
    else
        npm run format
    fi
}

# 清理构建文件
clean_build() {
    log_info "清理构建文件..."
    
    rm -rf build/
    rm -rf node_modules/.cache/
    
    log_info "清理完成"
}

# 主逻辑
main() {
    log_info "翻译系统前端启动脚本"
    log_info "命令: $COMMAND"
    
    # 基本检查
    check_node
    check_package_manager
    
    case $COMMAND in
        "install")
            install_dependencies
            ;;
        "dev")
            check_dependencies
            start_dev
            ;;
        "build")
            check_dependencies
            build_prod
            ;;
        "test")
            check_dependencies
            run_tests
            ;;
        "lint")
            check_dependencies
            run_lint
            ;;
        "format")
            check_dependencies
            run_format
            ;;
        "clean")
            clean_build
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 信号处理
trap 'log_info "收到中断信号，正在停止..."; exit 0' INT TERM

# 执行主逻辑
main "$@"
