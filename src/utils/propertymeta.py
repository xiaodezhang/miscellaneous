# 属性元类, 主要有两个功能:
# * 自动添加属性
# * 数据库映射
# 我们扩展了一些类型的注册
from uuid import uuid4
from PySide6.QtCore import QObject, Signal
from enum import Enum
import sqlite3
import datetime

from loguru import logger

DBStatus = Enum('DBStatus', ['IDLE', 'INSERT', 'UPDATE', 'DELETE'])

def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()

def adapt_datetime_iso(val):
    """Adapt datetime.datetime to timezone-naive ISO 8601 date."""
    return val.isoformat()

def adapt_timedelta(val):
    return val.total_seconds()

def adapt_bool(val):
    return 1 if val else 0

sqlite3.register_adapter(datetime.date, adapt_date_iso)
sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)
sqlite3.register_adapter(datetime.timedelta, adapt_timedelta)
sqlite3.register_adapter(bool, adapt_bool)

def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val.decode())

def convert_datetime(val):
    """Convert ISO 8601 datetime to datetime.datetime object."""
    return datetime.datetime.fromisoformat(val.decode())

def convert_timedelta(val):
    return datetime.timedelta(seconds=float(val))

def convert_bool(val):
    return True if int(val) == 1 else False

sqlite3.register_converter("date", convert_date)
sqlite3.register_converter("datetime", convert_datetime)
sqlite3.register_converter("timedelta", convert_timedelta)
sqlite3.register_converter("bool", convert_bool)

class PropertyMeta(type(QObject)):
    registry = []
    def __new__(cls, name, bases, dct, description):
        # cls是PropertyMeta对象, type的一个实例,
        # cls_instance是Class的对象, PropertyMeta的一个实例
        dct['description'] = description
        # 类实例集合
        dct['inses'] = []
        # 所有信号, 包含用户自定义的信号
        signals = {k: v for k, v in dct.items() if isinstance(v, Signal)}
        # 属性变动信号, 自动生成
        changed_signals = {}

        cls_instance = super().__new__(cls, name, bases, dct)
        # 注册类对象
        cls.registry.append(cls_instance)

        # 反射get和set方法
        def add_property(property_name, dtype):
            def type_name(dtype):
                match dtype:
                    case 'TEXT':
                        return str.__name__
                    case 'INTEGER':
                        return int.__name__
                    case 'REAL':
                        return float.__name__
                    case 'BLOB':
                        return bytes.__name__
                    case 'date':
                        return datetime.date.__name__
                    case 'datetime':
                        return datetime.datetime.__name__
                    case 'timedelta':
                        return datetime.timedelta.__name__
                    case _:
                        return dtype

            #私有成员
            private_name = "_" + property_name
            def getter(self):
                return self._properties.get(private_name)

            def setter(self, value):
                # 强类型检测
                assert (
                    type(value).__name__ == type_name(dtype) or value == None
                ), f"wrong type: {type(value)}, required: {type_name(dtype)}, value: {value}"
                if self._properties.get(private_name) == value:
                    return
                self._properties[private_name] = value
                if self.db_status != DBStatus.INSERT:
                    self.db_status = DBStatus.UPDATE
                signal = getattr(self, f"{property_name}_changed")
                assert signal
                signal.emit()
                self.changed.emit()

            setattr(cls_instance, property_name, property(getter, setter))
            # 添加属性变动的信号
            signal = Signal()
            setattr(cls_instance, f'{property_name}_changed', signal)
            signals.update({f'{property_name}_changed': signal})
            changed_signals.update({f'{property_name}_changed': signal})

        for property_name, dtype in description.items():
            add_property(property_name, dtype)

        def add_inner_property(name):
            def getter(self):
                return getattr(self, f'_{name}')
            def setter(self, value):
                setattr(self, f'_{name}', value)
            setattr(cls_instance, name, property(getter, setter))
        # 增加额外的属性维护数据库状态
        add_inner_property('id')
        add_inner_property('db_status')

        setattr(cls_instance, 'signals', signals)
        setattr(cls_instance, 'changed_signals', changed_signals)
        setattr(cls_instance, 'changed', Signal())

        def adapt(val):
            return val.id

        def converter(val):
            # note: 虽然adapt表明id为int, 但是这里的val却是bytes, 需要强制转换
            # load确保所有实例都已经完成初始化
            return next(x for x in dct['inses'] if x.id == int(val))

        # 注册转换器
        sqlite3.register_adapter(cls_instance, adapt)
        sqlite3.register_converter(name, converter)

        return cls_instance

    def __call__(cls, *args, **kwds):
        ins = cls.__new__(cls, *args, **kwds) #type: ignore
        # 添加属性集合
        setattr(ins, '_properties', {})
        setattr(ins, 'id', uuid4().int%(1<<32))
        setattr(ins, 'db_status', DBStatus.INSERT)
        if isinstance(ins, cls):
            ins.__init__(*args, **kwds)
        inses = getattr(cls, 'inses')
        inses.append(ins)
        return ins

# 数据库载入
def load(path):
    with sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES) as con:
        cur = con.cursor()
        for cls in PropertyMeta.registry:
            cols = "id INTEGER PRIMARY KEY"
            cols += "".join([f", {col} {dtype}" 
                for col, dtype in cls.description.items()])
            cls_name = cls.__name__
            cur.execute(f"CREATE TABLE IF NOT EXISTS {cls_name}({cols})")
            # 创建所有实例
            for row in cur.execute(f"SELECT id FROM {cls_name}"):
                ins = cls()
                ins.db_status = DBStatus.IDLE
                ins.id = row[0]
        con.commit()

        for cls in PropertyMeta.registry:
            cls_name = cls.__name__
            # 实例设置属性, 实例间存在引用关系, 故需先全部实例化
            for ins, row in zip(
                cls.inses
                , cur.execute(f"SELECT * FROM {cls_name}").fetchall()
            ):
                for k, v in zip(cls.description, row[1:]):
                    setattr(ins, k, v)
                convert = getattr(ins, 'convert', None)
                if convert:
                    convert()
# 数据库保存
def save(path):
    with sqlite3.connect(path) as con:
        def filter(cls, status):
            return [x for x in cls.inses if x.db_status == status]

        cur = con.cursor()
        for cls in PropertyMeta.registry:
            to_insert = filter(cls, DBStatus.INSERT)
            to_delete = filter(cls, DBStatus.DELETE)
            to_update = filter(cls, DBStatus.UPDATE)
            cls_name = cls.__name__

            for ins in cls.inses:
                adapt = getattr(ins, 'adapt', None)
                if adapt:
                    adapt()

            if to_delete: 
                cur.executemany(f"""
                    DELETE FROM {cls_name}
                    WHERE id = ?
                """, [(c.id,) for c in to_delete])

            if cls_name == 'Patient':
                logger.debug(f"to insert: {len(to_insert)}, all: {len(cls.inses)}")
            if to_insert:
                place_holder = ('?,'*(len(cls.description)+1))[:-1]
                cur.executemany(f"""
                    INSERT INTO {cls_name} VALUES({place_holder})
                """, [(x.id,)+tuple(getattr(x, p) for p in cls.description)
                        for x in to_insert])

            if to_update: 
                columns = ", ".join([f"{p} = ?" for p in cls.description])
                cur.executemany(f"""
                    UPDATE {cls_name}
                    SET {columns}
                    where id = ?
                """, [tuple(getattr(x, p) for p in cls.description) + (x.id,)
                        for x in to_update])

            for x in cls.inses:
                x.db_status = DBStatus.IDLE

        con.commit()
