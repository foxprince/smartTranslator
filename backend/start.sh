#!/bin/bash

# 翻译系统启动脚本
# 提供多种启动方式和环境配置

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

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
翻译系统启动脚本

用法: $0 [选项] [命令]

命令:
    dev         开发模式启动（自动重载）
    prod        生产模式启动
    docker      Docker模式启动
    test        测试模式启动
    init        初始化系统
    stop        停止服务
    restart     重启服务
    status      查看服务状态
    logs        查看日志
    backup      创建备份
    monitor     启动监控

选项:
    -h, --help      显示帮助信息
    -e, --env       指定环境文件 (默认: .env)
    -p, --port      指定端口 (默认: 8000)
    -w, --workers   指定工作进程数 (默认: 1)
    -d, --daemon    后台运行
    -v, --verbose   详细输出
    --no-reload     禁用自动重载
    --no-check      跳过健康检查

示例:
    $0 dev                    # 开发模式启动
    $0 prod -w 4 -d          # 生产模式，4个工作进程，后台运行
    $0 docker                # Docker模式启动
    $0 init                  # 初始化系统
    $0 backup                # 创建备份

EOF
}

# 默认配置
ENVIRONMENT="development"
ENV_FILE=".env"
PORT=8000
WORKERS=1
DAEMON=false
VERBOSE=false
RELOAD=true
HEALTH_CHECK=true
COMMAND=""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--env)
            ENV_FILE="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -d|--daemon)
            DAEMON=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-reload)
            RELOAD=false
            shift
            ;;
        --no-check)
            HEALTH_CHECK=false
            shift
            ;;
        dev|prod|docker|test|init|stop|restart|status|logs|backup|monitor)
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

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(echo "$python_version < 3.9" | bc -l) -eq 1 ]]; then
        log_error "需要Python 3.9或更高版本，当前版本: $python_version"
        exit 1
    fi
    
    log_info "Python版本: $python_version"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if [[ ! -f "requirements.txt" ]]; then
        log_error "requirements.txt 文件不存在"
        exit 1
    fi
    
    # 检查虚拟环境
    if [[ ! -d "venv" ]]; then
        log_warn "虚拟环境不存在，正在创建..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    pip install -r requirements.txt > /dev/null 2>&1
    
    log_info "依赖检查完成"
}

# 加载环境变量
load_environment() {
    if [[ -f "$ENV_FILE" ]]; then
        log_info "加载环境变量: $ENV_FILE"
        export $(grep -v '^#' "$ENV_FILE" | xargs)
    else
        log_warn "环境文件不存在: $ENV_FILE"
    fi
}

# 检查数据库连接
check_database() {
    if [[ "$HEALTH_CHECK" == "false" ]]; then
        return 0
    fi
    
    log_info "检查数据库连接..."
    
    python3 -c "
import sys
sys.path.append('.')
try:
    from app.core.database import engine
    print('数据库连接正常')
except Exception as e:
    print(f'数据库连接失败: {e}')
    sys.exit(1)
" || {
        log_error "数据库连接失败"
        exit 1
    }
}

# 初始化系统
init_system() {
    log_info "初始化系统..."
    
    # 创建必要的目录
    mkdir -p logs monitoring backups config
    
    # 初始化数据库
    python3 scripts/init_db.py init
    
    # 生成配置文件
    python3 scripts/config_manager.py init
    
    log_info "系统初始化完成"
}

# 开发模式启动
start_dev() {
    log_info "启动开发模式..."
    
    UVICORN_CMD="uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    
    if [[ "$RELOAD" == "true" ]]; then
        UVICORN_CMD="$UVICORN_CMD --reload"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        UVICORN_CMD="$UVICORN_CMD --log-level debug"
    fi
    
    if [[ "$DAEMON" == "true" ]]; then
        nohup $UVICORN_CMD > logs/app.log 2>&1 &
        echo $! > .pid
        log_info "服务已在后台启动，PID: $(cat .pid)"
    else
        exec $UVICORN_CMD
    fi
}

# 生产模式启动
start_prod() {
    log_info "启动生产模式..."
    
    GUNICORN_CMD="gunicorn app.main:app"
    GUNICORN_CMD="$GUNICORN_CMD --workers $WORKERS"
    GUNICORN_CMD="$GUNICORN_CMD --worker-class uvicorn.workers.UvicornWorker"
    GUNICORN_CMD="$GUNICORN_CMD --bind 0.0.0.0:$PORT"
    GUNICORN_CMD="$GUNICORN_CMD --timeout 30"
    GUNICORN_CMD="$GUNICORN_CMD --keepalive 2"
    GUNICORN_CMD="$GUNICORN_CMD --max-requests 1000"
    GUNICORN_CMD="$GUNICORN_CMD --max-requests-jitter 100"
    GUNICORN_CMD="$GUNICORN_CMD --preload"
    
    if [[ "$VERBOSE" == "true" ]]; then
        GUNICORN_CMD="$GUNICORN_CMD --log-level debug"
    fi
    
    if [[ "$DAEMON" == "true" ]]; then
        GUNICORN_CMD="$GUNICORN_CMD --daemon --pid .pid"
        GUNICORN_CMD="$GUNICORN_CMD --access-logfile logs/access.log"
        GUNICORN_CMD="$GUNICORN_CMD --error-logfile logs/error.log"
    fi
    
    exec $GUNICORN_CMD
}

# Docker模式启动
start_docker() {
    log_info "启动Docker模式..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 构建并启动服务
    docker-compose up --build -d
    
    log_info "Docker服务已启动"
    log_info "API地址: http://localhost:$PORT"
    log_info "监控面板: http://localhost:3001 (admin/admin)"
    log_info "日志查看: http://localhost:5601"
}

# 测试模式启动
start_test() {
    log_info "启动测试模式..."
    
    export TESTING=true
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_translation_db"
    
    # 运行测试
    python3 run_tests.py --coverage
}

# 停止服务
stop_service() {
    log_info "停止服务..."
    
    if [[ -f ".pid" ]]; then
        PID=$(cat .pid)
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm .pid
            log_info "服务已停止"
        else
            log_warn "服务未运行"
            rm .pid
        fi
    else
        # 尝试通过端口查找进程
        PID=$(lsof -ti:$PORT)
        if [[ -n "$PID" ]]; then
            kill "$PID"
            log_info "服务已停止"
        else
            log_warn "未找到运行的服务"
        fi
    fi
    
    # 停止Docker服务
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose down
    fi
}

# 重启服务
restart_service() {
    log_info "重启服务..."
    stop_service
    sleep 2
    
    case $ENVIRONMENT in
        "development")
            start_dev
            ;;
        "production")
            start_prod
            ;;
        *)
            start_dev
            ;;
    esac
}

# 查看服务状态
show_status() {
    log_info "服务状态:"
    
    if [[ -f ".pid" ]]; then
        PID=$(cat .pid)
        if kill -0 "$PID" 2>/dev/null; then
            echo "  状态: 运行中"
            echo "  PID: $PID"
            echo "  端口: $PORT"
        else
            echo "  状态: 已停止"
            rm .pid
        fi
    else
        PID=$(lsof -ti:$PORT 2>/dev/null)
        if [[ -n "$PID" ]]; then
            echo "  状态: 运行中"
            echo "  PID: $PID"
            echo "  端口: $PORT"
        else
            echo "  状态: 未运行"
        fi
    fi
    
    # 检查Docker服务
    if command -v docker &> /dev/null && docker-compose ps &> /dev/null; then
        echo ""
        echo "Docker服务状态:"
        docker-compose ps
    fi
}

# 查看日志
show_logs() {
    log_info "查看日志..."
    
    if [[ -f "logs/app.log" ]]; then
        tail -f logs/app.log
    elif [[ -f "logs/error.log" ]]; then
        tail -f logs/error.log
    else
        log_warn "未找到日志文件"
        
        # 查看Docker日志
        if command -v docker-compose &> /dev/null; then
            docker-compose logs -f backend
        fi
    fi
}

# 创建备份
create_backup() {
    log_info "创建备份..."
    python3 scripts/backup_restore.py backup --full
}

# 启动监控
start_monitor() {
    log_info "启动监控..."
    python3 scripts/monitor.py &
    echo $! > .monitor.pid
    log_info "监控已启动，PID: $(cat .monitor.pid)"
}

# 主逻辑
main() {
    log_info "翻译系统启动脚本"
    log_info "命令: $COMMAND"
    
    # 基本检查
    check_python
    
    case $COMMAND in
        "init")
            check_dependencies
            load_environment
            init_system
            ;;
        "dev")
            check_dependencies
            load_environment
            check_database
            start_dev
            ;;
        "prod")
            ENVIRONMENT="production"
            check_dependencies
            load_environment
            check_database
            start_prod
            ;;
        "docker")
            start_docker
            ;;
        "test")
            check_dependencies
            start_test
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "backup")
            create_backup
            ;;
        "monitor")
            start_monitor
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 信号处理
trap 'log_info "收到中断信号，正在停止..."; stop_service; exit 0' INT TERM

# 执行主逻辑
main "$@"
