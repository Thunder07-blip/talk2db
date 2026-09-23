import unittest
import asyncio
import json
from app.main import app


class TestAPI(unittest.TestCase):

    def _asgi_request(self, method: str, path: str):
        scope = {
            "type": "http",
            "method": method,
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": [],
        }
        body = b""
        status = None

        async def receive():
            return {"type": "http.request"}

        async def send(message):
            nonlocal body, status
            if message["type"] == "http.response.start":
                status = message["status"]
            elif message["type"] == "http.response.body":
                body += message.get("body", b"")

        asyncio.run(app(scope, receive, send))
        try:
            parsed_body = json.loads(body.decode()) if body else None
        except json.JSONDecodeError:
            parsed_body = body
        return status, parsed_body

    def test_root_endpoint(self):
        status, body = self._asgi_request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"<!DOCTYPE html>", body)

    def test_tables_endpoint(self):
        status, body = self._asgi_request("GET", "/tables")
        self.assertEqual(status, 200)
        self.assertIn("tables", body)
        self.assertIn("Artist", body["tables"])
        self.assertIn("Album", body["tables"])

    def test_schema_endpoint_valid_table(self):
        status, body = self._asgi_request("GET", "/schema/Artist")
        self.assertEqual(status, 200)
        self.assertEqual(body["table"], "Artist")
        self.assertIsInstance(body["columns"], list)
        self.assertIsInstance(body["foreign_keys"], list)

    def test_schema_endpoint_not_found(self):
        status, body = self._asgi_request("GET", "/schema/NonExistentTable")
        self.assertEqual(status, 404)
        self.assertIn("detail", body)


if __name__ == "__main__":
    unittest.main()
