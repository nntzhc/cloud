# 项目规则和最佳实践

## Python 脚本执行规则

### 本项目特定配置

当需要运行Python脚本时，AI助手应该：

1. **优先使用conda环境的完整Python路径**:
   ```powershell
   
   # 优先直接使用完整的 Python 路径运行 Web 服务器。
   & "D:\Installations\Anaconda3\envs\AI\python.exe" script.py
   ```
   如果不存在上述的路径,则使用下面的 Python 路径运行脚本
   ```powershell
   & "D:\installation\Anaconda\python.exe" script.py
   ```
2. 临时使用的的测试文件、配置文件等应当运行后主动删除

