# Test Client

### HTTP Test Client

Test client allows you to make requests to your routes. It uses [httpx](https://www.python-httpx.org/).

`test_client(base_url="http://testserver")`

- `base_url` - example hostname for testing.

```python
app = Yaat()

@app.route("/")
def index(request):
    ...

test_client = app.test_client()
response = await client.get("/")
```

[read more about httpx functionalities](https://www.python-httpx.org/quickstart/)
