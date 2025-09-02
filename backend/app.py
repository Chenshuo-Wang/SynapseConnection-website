# --- backend/app.py (云端草稿版) ---

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.utils import secure_filename

# --- 基础配置 ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'a_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "your-super-secret-key-change-this"
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

jwt = JWTManager(app)
db = SQLAlchemy(app)

# --- 数据库模型 ---
# --- 修复后的 User 模型 ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    
    # 【关键】新增下面这一行，告诉 User 它可以拥有多个 Idea
    ideas = db.relationship('Idea', backref='user', lazy=True)
    
    # 草稿的关系保持不变
    draft = db.relationship('Draft', backref='user_draft', uselist=False, cascade="all, delete-orphan")

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    # 关系保持不变，只是为了清晰，把 user 属性删掉，因为 backref 已经创建了
    # user = db.relationship('User', backref=db.backref('ideas', lazy=True))

# 2. 新增：草稿数据模型
class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)


# --- API 接口 ---
# ... (register, login, upload, uploaded_file 接口保持不变) ...
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'): return jsonify({"message": "邮箱和密码不能为空！"}), 400
    if User.query.filter_by(email=data['email']).first(): return jsonify({"message": "这个邮箱已经被注册了！"}), 400
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data.get('username', data['email']), email=data['email'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "用户注册成功！"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'): return jsonify({"message": "邮箱和密码不能为空！"}), 400
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']): return jsonify({"message": "邮箱或密码错误！"}), 401
    access_token = create_access_token(identity=user.email)
    return jsonify(access_token=access_token), 200

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files: return jsonify({"message": "请求中没有文件部分"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"message": "没有选择文件"}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "文件上传成功", "filename": filename}), 200

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ... (submit_idea, get_ideas, get_idea_detail 接口暂时保持不变，但之后我们会修改 submit_idea) ...
@app.route('/api/ideas', methods=['POST'])
@jwt_required()
def submit_idea():
    # 【修改开始】
    # 1. 从 request.form 改为 request.get_json()
    data = request.get_json()

    # 2. 增加一个健壮性检查，防止前端发送空数据
    if not data:
        return jsonify({"message": "请求体不能为空！"}), 400

    # 3. 从 data 字典中获取数据
    title = data.get('title')
    content = data.get('content')
    image_filename = data.get('image_filename') # image_filename 也来自 JSON
    # 【修改结束】

    # 下面的逻辑保持不变
    if not title or not content: 
        return jsonify({"message": "标题和内容不能为空！"}), 400
    
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    new_idea = Idea(title=title, content=content, user_id=user.id, image_filename=image_filename)
    
    db.session.add(new_idea)
    
    # 【关键补充】在提交 idea 成功后，删除对应的云端草稿
    if user.draft:
        db.session.delete(user.draft)

    db.session.commit()
    
    return jsonify({"message": "Idea提交成功！"}), 201


@app.route('/api/ideas', methods=['GET'])
def get_ideas():
    all_ideas = Idea.query.order_by(Idea.created_at.desc()).all()
    ideas_list = []
    for idea in all_ideas:
        ideas_list.append({ 'id': idea.id, 'title': idea.title, 'content_summary': (idea.content[:100] + '...') if len(idea.content) > 100 else idea.content, 'author': idea.user.username, 'created_at': idea.created_at.strftime('%Y-%m-%d %H:%M'), 'image_url': f"/uploads/{idea.image_filename}" if idea.image_filename else None })
    return jsonify(ideas_list), 200

@app.route('/api/ideas/<int:idea_id>', methods=['GET'])
def get_idea_detail(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    idea_detail = { 'id': idea.id, 'title': idea.title, 'content': idea.content, 'author': idea.user.username, 'created_at': idea.created_at.strftime('%Y-%m-%d %H:%M'), 'image_url': f"/uploads/{idea.image_filename}" if idea.image_filename else None }
    return jsonify(idea_detail), 200

# 3. 新增：云端草稿的三个API接口
@app.route('/api/draft', methods=['GET'])
@jwt_required()
def get_draft():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    if user.draft:
        return jsonify({
            'title': user.draft.title,
            'content': user.draft.content
        }), 200
    return jsonify(None), 200 # 返回 null 表示没有草稿

@app.route('/api/draft', methods=['POST'])
@jwt_required()
def save_draft():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    data = request.get_json()

    if user.draft:
        # 如果草稿已存在，则更新
        user.draft.title = data.get('title', '')
        user.draft.content = data.get('content', '')
    else:
        # 如果草稿不存在，则创建
        new_draft = Draft(
            title=data.get('title', ''),
            content=data.get('content', ''),
            user_id=user.id
        )
        db.session.add(new_draft)
    
    db.session.commit()
    return jsonify({"message": "草稿已保存到云端"}), 200

@app.route('/api/draft', methods=['DELETE'])
@jwt_required()
def delete_draft():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    if user.draft:
        db.session.delete(user.draft)
        db.session.commit()
    return jsonify({"message": "云端草稿已清除"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)