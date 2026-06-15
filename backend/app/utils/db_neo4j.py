import os
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Thiết lập logging cơ bản để dễ debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USERNAME", "neo4j")
        self.pwd = os.getenv("NEO4J_PASSWORD", "password")
        self.__driver = None

        try:
            # Khởi tạo driver kết nối
            self.__driver = GraphDatabase.driver(self.uri, auth=(self.user, self.pwd))
            self.__driver.verify_connectivity()
            logger.info("✅ Kết nối Neo4j thành công!")
        except Exception as e:
            logger.error(f"❌ Lỗi kết nối Neo4j: {e}")

    def close(self):
        """Đóng kết nối khi tắt app"""
        if self.__driver is not None:
            self.__driver.close()
            logger.info("Đã đóng kết nối Neo4j.")

    def query(self, query, parameters=None, db=None):
        """Hàm thực thi câu lệnh Cypher (Đọc/Ghi) chung"""
        assert self.__driver is not None, "Driver chưa được khởi tạo!"
        session = None
        response = None
        try:
            # Mở session, chạy query và ép kiểu kết quả về List các Dict
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            result = session.run(query, parameters)
            response = [record.data() for record in result]
        except Exception as e:
            logger.error(f"Lỗi khi chạy query: {e}")
            logger.error(f"Query text: {query}")
        finally:
            if session is not None:
                session.close()
        return response

# Khởi tạo một instance duy nhất (Singleton) để import ở các file khác
neo4j_db = Neo4jConnection()