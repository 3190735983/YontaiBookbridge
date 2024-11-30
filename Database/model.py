# 表设计，以3NF及以上为设计目标

# 用户主题：

# 用户信息表：uid,账号，密码，身份等
# 用户浏览记录表 只需要记忆 浏览过的文书的记录


# 文书主题:

# 文书数据表：编号，文本内容，契约人，大意……评论区
# 文书纠错表：用于管理员查看用户提交的文书的纠错内容


# 用户文书表：uid,编号,标记、笔记等

# 日志表 记录对文书数据表的更改日志
from sqlalchemy import Column, Integer, String, Text, Date, Enum, TIMESTAMP, ForeignKey 
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from Database.config import db  # 假设你在config.py中配置了db实例

# 文书类：Documents
class Documents(db.Model):
    __tablename__ = 'Documents'  # 定义表名为 'Documents'
    
    # 文书的基本字段
    DocumentID = Column(Integer, primary_key=True, autoincrement=True)  # 文书的唯一标识符，自增主键
    Title = Column(String(255), nullable=False)  # 文书标题，非空
    OriginalText = Column(Text, nullable=False)  # 文书的繁体原文，非空
    SimplifiedText = Column(Text, default=None)  # 文书的简体原文，默认为空
    Date = Column(Date, nullable=False)  # 标准化日期，非空
    RawDate = Column(String(100), default=None)  # 原始日期格式，默认为空
    DocumentType = Column(Enum('借贷', '契约', '其他'), nullable=False)  # 文书类型，限制为'借贷', '契约', '其他'中的一个
    Summary = Column(Text, default=None)  # 文书的大意，默认为空
    CreatedAt = Column(TIMESTAMP, default=func.current_timestamp())  # 创建时间，默认为当前时间戳
    UpdatedAt = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())  # 更新时间戳，自动更新为当前时间
    
    # 关系定义：
    participants = relationship('Participants', backref='document', cascade='all, delete-orphan')  # 与参与者表的关联，一对多关系
    metadata = relationship('Metadata', backref='document', cascade='all, delete-orphan')  # 与元数据表的关联，一对多关系
    highlights = relationship('Highlights', backref='document', cascade='all, delete-orphan')  # 与高亮表的关联，一对多关系
    notes = relationship('Notes', backref='document', cascade='all, delete-orphan')  # 与批注表的关联，一对多关系
    comments = relationship('Comments', backref='document', cascade='all, delete-orphan')  # 与评论表的关联，一对多关系
    corrections = relationship('Corrections', backref='document', cascade='all, delete-orphan')  # 与纠错表的关联，一对多关系
    history = relationship('History', backref='document', cascade='all, delete-orphan')  # 与历史记录表的关联，一对多关系

    # 定义索引：帮助优化查询
    __table_args__ = (
        db.Index('idx_DocumentType', 'DocumentType'),  # 为 DocumentType 创建索引
        db.Index('idx_CreatedAt', 'CreatedAt'),  # 为 CreatedAt 创建索引
    )


# 参与者类：Participants
class Participants(db.Model):
    __tablename__ = 'Participants'  # 表名为 'Participants'
    
    ParticipantID = Column(Integer, primary_key=True, autoincrement=True)  # 参与者的唯一标识符
    DocumentID = Column(Integer, ForeignKey('Documents.DocumentID'), nullable=False)  # 外键，关联到 'Documents' 表的 DocumentID
    Name = Column(String(255), nullable=False)  # 参与者姓名，非空
    Role = Column(String(50), nullable=False)  # 参与者的角色（如签署人、见证人），非空
    CreatedAt = Column(TIMESTAMP, default=func.current_timestamp())  # 参与者记录创建时间，默认为当前时间戳


# 用户类：Users
class Users(db.Model):
    __tablename__ = 'Users'  # 表名为 'Users'
    
    UserID = Column(Integer, primary_key=True, autoincrement=True)  # 用户的唯一标识符
    Username = Column(String(100), nullable=False, unique=True)  # 用户名，唯一，非空
    PasswordHash = Column(String(255), nullable=False)  # 密码的哈希值，非空
    Email = Column(String(150), nullable=False, unique=True)  # 用户邮箱，唯一，非空
    Role = Column(Enum('Admin', 'Member', 'NonMember'), nullable=False)  # 用户角色，'Admin'、'Member' 或 'NonMember'
    LoginAttempts = Column(Integer, default=0, nullable=False)  # 连续登录失败次数，默认为 0
    AccountStatus = Column(Enum('Active', 'Locked'), default='Active')  # 账户状态，默认为 'Active'
    CreatedAt = Column(TIMESTAMP, default=func.current_timestamp())  # 用户创建时间，默认为当前时间戳
    LastLogin = Column(TIMESTAMP, default=None)  # 上次登录时间，默认为空
    
    # 关系定义：
    highlights = relationship('Highlights', backref='user', cascade='all, delete-orphan')  # 用户与高亮记录的关联
    notes = relationship('Notes', backref='user', cascade='all, delete-orphan')  # 用户与批注记录的关联
    folders = relationship('Folders', backref='user', cascade='all, delete-orphan')  # 用户与收藏夹的关联
    corrections = relationship('Corrections', backref='user', cascade='all, delete-orphan')  # 用户与纠错记录的关联
    comments = relationship('Comments', backref='user', cascade='all, delete-orphan')  # 用户与评论记录的关联
    history = relationship('History', backref='user', cascade='all, delete-orphan')  # 用户与历史记录的关联


# 高亮类：Highlights
class Highlights(db.Model):
    __tablename__ = 'Highlights'  # 表名为 'Highlights'
    
    HighlightID = Column(Integer, primary_key=True, autoincrement=True)  # 高亮记录的唯一标识符
    DocumentID = Column(Integer, ForeignKey('Documents.DocumentID'), nullable=False)  # 外键，关联到 'Documents' 表的 DocumentID
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=False)  # 外键，关联到 'Users' 表的 UserID
    StartPosition = Column(Integer, nullable=False)  # 高亮起始位置（字符索引）
    EndPosition = Column(Integer, nullable=False)  # 高亮结束位置（字符索引）
    Color = Column(String(20), default='yellow')  # 高亮颜色，默认为 'yellow'
    CreatedAt = Column(TIMESTAMP, default=func.current_timestamp())  # 高亮操作时间，默认为当前时间戳


# 批注类：Notes
class Notes(db.Model):
    __tablename__ = 'Notes'  # 表名为 'Notes'
    
    NoteID = Column(Integer, primary_key=True, autoincrement=True)  # 批注记录的唯一标识符
    DocumentID = Column(Integer, ForeignKey('Documents.DocumentID'), nullable=False)  # 外键，关联到 'Documents' 表的 DocumentID
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=False)  # 外键，关联到 'Users' 表的 UserID
    AnnotationText = Column(Text, nullable=False)  # 批注内容，非空
    StartPosition = Column(Integer, nullable=False)  # 批注起始位置（字符索引）
    EndPosition = Column(Integer, nullable=False)  # 批注结束位置（字符索引）
    CreatedAt = Column(TIMESTAMP, default=func.current_timestamp())  # 批注创建时间，默认为当前时间戳


# 收藏夹类：Folders
class Folders(db.Model):
    __tablename__ = 'Folders'  # 表名为 'Folders'
    
    FolderID = Column(Integer, primary_key=True, autoincrement=True)  # 收藏夹的唯一标识符
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=False)  # 外键，关联到 'Users' 表的 UserID
    ParentFolderID = Column(Integer, ForeignKey('Folders.FolderID'), nullable=True)  # 父级收藏夹ID，用于创建层级关系
    FolderName = Column(String(255), nullable=False)  # 收藏夹名称，非空
    CreatedAt = Column(TIMESTAMP, default=func.current_timestamp())  # 收藏夹创建时间，默认为当前时间戳


# 审计日志类：AuditLog
class AuditLog(db.Model):
    __tablename__ = 'AuditLog'  # 表名为 'AuditLog'
    
    AuditID = Column(Integer, primary_key=True, autoincrement=True)  # 审计记录的唯一标识符
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=True)  # 外键，关联到 'Users' 表的 UserID（可为空）
    ActionType = Column(String(50), nullable=False)  # 操作类型（如创建、更新等），非空
    ActionDescription = Column(Text, nullable=False)  # 操作的详细描述，非空
    TargetTable = Column(String(50), nullable=True)  # 被操作的表名（可为空）
    TargetID = Column(Integer, nullable=True)  # 被操作的记录ID（可为空）
    Timestamp = Column(TIMESTAMP, default=func.current_timestamp())  # 操作时间，默认为当前时间戳
    IPAddress = Column(String(45), nullable=True)  # 操作的IP地址（可为空）


# 纠错类：Corrections
class Corrections(db.Model):
    __tablename__ = 'Corrections'  # 表名为 'Corrections'
    
    CorrectionID = Column(Integer, primary_key=True, autoincrement=True)  # 纠错记录的唯一标识符
    DocumentID = Column(Integer, ForeignKey('Documents.DocumentID'), nullable=False)  # 外键，关联到 'Documents' 表的 DocumentID
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=True)  # 外键，关联到 'Users' 表的 UserID（可为空）
    CorrectionText = Column(Text, nullable=False)  # 纠错内容，非空
    CreatedAt = Column(TIMESTAMP, default=func.current_timestamp())  # 纠错提交时间，默认为当前时间戳


# 评论类：Comments
class Comments(db.Model):
    __tablename__ = 'Comments'  # 表名为 'Comments'
    
    CommentID = Column(Integer, primary_key=True, autoincrement=True)  # 评论记录的唯一标识符
    DocumentID = Column(Integer, ForeignKey('Documents.DocumentID'), nullable=False)  # 外键，关联到 'Documents' 表的 DocumentID
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=True)  # 外键，关联到 'Users' 表的 UserID（可为空）
    CommentText = Column(Text, nullable=False)  # 评论内容，非空
    CreatedAt = Column(TIMESTAMP, default=func.current_timestamp())  # 评论创建时间，默认为当前时间戳


# 浏览记录类：History
class History(db.Model):
    __tablename__ = 'History'  # 表名为 'History'
    
    HistoryID = Column(Integer, primary_key=True, autoincrement=True)  # 浏览记录的唯一标识符
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=False)  # 外键，关联到 'Users' 表的 UserID
    DocumentID = Column(Integer, ForeignKey('Documents.DocumentID'), nullable=False)  # 外键，关联到 'Documents' 表的 DocumentID
    ViewedAt = Column(TIMESTAMP, default=func.current_timestamp())  # 浏览时间，默认为当前时间戳

