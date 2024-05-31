from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import urllib.parse

# 自动获取图片目录
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
root_dir = f'{current_directory}/'  

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # 解析请求的路径
        # path = self.path.strip('/')
        # file_path = os.path.normpath(os.path.join(root_dir, path))
        path = urllib.parse.unquote(self.path.strip('/'))
        print(path)
        file_path = os.path.normpath(os.path.join(root_dir, path))

        # 安全检查：确保请求的文件在根目录内
        if not os.path.commonprefix([root_dir, file_path]) == root_dir:
            self.send_error(403, "Forbidden")
            return

        # 检查文件是否存在
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')  # 根据图片类型调整
            self.end_headers()
            with open(file_path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            print(file_path)
            self.send_error(404, "File not found")

# 设置服务器地址和端口
address = ('', 5999)  # 空字符串代表接受所有接口，端口为5999

# 创建服务器实例
httpd = HTTPServer(address, SimpleHTTPRequestHandler)

# 启动服务器
print("Serving at port 5999...")
httpd.serve_forever()
